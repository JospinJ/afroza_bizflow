import { ChatDemo } from "@/components/ChatDemo";

type PageProps = {
  params: Promise<{ slug: string }>;
};

export default async function AgentPage({ params }: PageProps) {
  const { slug } = await params;
  return <ChatDemo slug={slug} />;
}
