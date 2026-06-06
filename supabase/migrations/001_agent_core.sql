-- Agent IA core schema (B1-B6)
-- Run in Supabase SQL Editor or: python scripts/setup_db.py (with SUPABASE_DB_PASSWORD)

-- Businesses (PME profile)
create table if not exists businesses (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid references auth.users(id),  name text not null,
  sector text,
  city text,
  country text default 'CI',
  tone text default 'professionnel',
  language text default 'fr',
  public_slug text unique not null,
  plan text default 'free',
  status text default 'active',
  config jsonb default '{}'::jsonb,
  created_at timestamptz default now()
);

-- Knowledge base for RAG
create table if not exists knowledge_items (
  id uuid primary key default gen_random_uuid(),
  business_id uuid not null references businesses(id) on delete cascade,
  type text not null check (type in ('service', 'faq', 'policy', 'hours', 'tone')),
  title text not null,
  content text not null,
  source text default 'onboarding',
  confidence float default 1.0,
  active boolean default true,
  created_at timestamptz default now()
);

create index idx_knowledge_business on knowledge_items(business_id, type) where active = true;

-- Customers (multichannel identity)
create table if not exists customers (
  id uuid primary key default gen_random_uuid(),
  business_id uuid not null references businesses(id) on delete cascade,
  name text,
  phone text,
  email text,
  channel_ids jsonb default '{}'::jsonb,
  tags text[] default '{}',
  reliability_score int default 50,
  created_at timestamptz default now()
);

-- Conversations (unified history B6)
create table if not exists conversations (
  id uuid primary key default gen_random_uuid(),
  business_id uuid not null references businesses(id) on delete cascade,
  customer_id uuid references customers(id),
  channel text not null check (channel in ('web', 'telegram', 'sms', 'whatsapp_manual')),
  status text default 'open' check (status in ('open', 'escalated', 'closed')),
  summary text,
  metadata jsonb default '{}'::jsonb,
  last_message_at timestamptz default now(),
  created_at timestamptz default now()
);

-- Messages with intent tracking (B2)
create table if not exists messages (
  id uuid primary key default gen_random_uuid(),
  conversation_id uuid not null references conversations(id) on delete cascade,
  direction text not null check (direction in ('inbound', 'outbound')),
  content text not null,
  intent text,
  confidence float,
  raw_payload jsonb,
  created_at timestamptz default now()
);

create index idx_messages_conversation on messages(conversation_id, created_at);

-- Leads (B3 qualification output)
create table if not exists leads (
  id uuid primary key default gen_random_uuid(),
  business_id uuid not null references businesses(id) on delete cascade,
  customer_id uuid references customers(id),
  need text,
  budget numeric,
  deadline date,
  location text,
  score int default 50,
  source text default 'agent',
  status text default 'new' check (status in ('new', 'qualifying', 'qualified', 'lost')),
  created_at timestamptz default now()
);

-- Deals (pipeline link)
create table if not exists deals (
  id uuid primary key default gen_random_uuid(),
  business_id uuid not null references businesses(id) on delete cascade,
  customer_id uuid references customers(id),
  lead_id uuid references leads(id),
  stage text default 'prospect',
  amount numeric,
  expected_close date,
  priority int default 50,
  created_at timestamptz default now()
);

-- Appointments (B4)
create table if not exists appointments (
  id uuid primary key default gen_random_uuid(),
  business_id uuid not null references businesses(id) on delete cascade,
  customer_id uuid references customers(id),
  conversation_id uuid references conversations(id),
  service text not null,
  start_at timestamptz not null,
  end_at timestamptz not null,
  status text default 'pending' check (status in ('pending', 'confirmed', 'cancelled', 'completed')),
  reminder_status text default 'pending',
  created_at timestamptz default now()
);

-- Seed: Salon Aïcha demo data (run after creating a test owner or use service role)
-- INSERT INTO businesses (name, sector, city, tone, public_slug) VALUES
--   ('Salon Aïcha', 'coiffure', 'Abidjan', 'chaleureux', 'salon-aicha');
