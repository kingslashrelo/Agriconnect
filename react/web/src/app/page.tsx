"use client";

import { useAuth } from "@/lib/auth-context";
import { LandingPage } from "@/components/LandingPage";
import { HomeDashboard } from "@/components/HomeDashboard";

export default function Page() {
  const { user, ready } = useAuth();
  if (!ready) return null;
  if (!user) return <LandingPage />;
  return <HomeDashboard />;
}
