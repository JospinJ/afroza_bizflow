-- Seed Salon Aïcha (demo Agent IA)
-- Exécuter dans Supabase SQL Editor APRÈS 001_agent_core.sql

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
