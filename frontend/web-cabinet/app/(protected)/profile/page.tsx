import { getServerSession } from "next-auth";
import { redirect } from "next/navigation";
import { authOptions } from "@/app/api/auth/[...nextauth]/route";

export default async function ProfilePage() {
  const session = await getServerSession(authOptions);
  if (!session) redirect("/login");

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-semibold">Профіль ФОП</h1>
      <div className="rounded-lg border p-4 space-y-2">
        <div>Імʼя: {session.user?.name}</div>
        <div>Email: {session.user?.email}</div>
      </div>
    </div>
  );
}


