-- Afroza BizFlow — exécuter TOUT ce fichier dans Supabase SQL Editor (Run)

-- === 001_agent_core.sql ===

create table if not exists businesses (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid references auth.users(id),
  name text not null,
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

create index if not exists idx_knowledge_business on knowledge_items(business_id, type) where active = true;

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

create index if not exists idx_messages_conversation on messages(conversation_id, created_at);

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

-- === 002_seed_salon_aicha.sql ===

insert into businesses (name, sector, city, tone, language, public_slug, country)
values ('Salon Aïcha', 'coiffure', 'Abidjan', 'chaleureux', 'fr', 'salon-aicha', 'CI')
on conflict (public_slug) do nothing;

insert into knowledge_items (business_id, type, title, content)
select b.id, v.type, v.title, v.content
from businesses b
cross join (values
  ('service', 'Braids', '15000 FCFA, durée 3h, acompte 5000 FCFA'),
  ('service', 'Tissage', '12000 FCFA, durée 2h30'),
  ('hours', 'Horaires', 'Lundi-Samedi 9h-19h, Dimanche fermé'),
  ('policy', 'Acompte', '50% à la réservation, annulation 24h avant'),
  ('faq', 'Paiement', 'Mobile Money accepté. Mode simulation active en démo.')
) as v(type, title, content)
where b.public_slug = 'salon-aicha'
and not exists (
  select 1 from knowledge_items k
  where k.business_id = b.id and k.title = v.title
);
