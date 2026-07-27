"use client";

import { ExternalLink, KeyRound, Loader2,Mail, Shield, UserPlus, Users } from "lucide-react";
import { useCallback,useEffect, useState } from "react";
import { toast } from "sonner";

import { TelemetrySection } from "@/components/TelemetrySection";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useAuth } from "@/lib/auth";

export default function SettingsPage() {
  const auth = useAuth();
  const [admins, setAdmins] = useState<{ id: number; email: string }[]>([]);
  const [loadingAdmins, setLoadingAdmins] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [newEmail, setNewEmail] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [addingAdmin, setAddingAdmin] = useState(false);

  const fetchAdmins = useCallback(async () => {
    try {
      setLoadingAdmins(true);
      const token = await auth.getAccessToken();
      const res = await fetch("/api/v1/user/admins", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (res.ok) {
        const data = await res.json();
        setAdmins(data);
      }
    } catch (e) {
      console.error("Failed to fetch admins", e);
    } finally {
      setLoadingAdmins(false);
    }
  }, [auth]);

  useEffect(() => {
    fetchAdmins();
  }, [fetchAdmins]);

  const handleAddAdmin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newEmail || !newPassword) return;

    if (newPassword.length < 8) {
      toast.error("Password must be at least 8 characters");
      return;
    }

    try {
      setAddingAdmin(true);
      const token = await auth.getAccessToken();
      const res = await fetch("/api/v1/user/admins", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email: newEmail, password: newPassword }),
      });

      if (res.ok) {
        toast.success("Admin account added successfully!");
        setNewEmail("");
        setNewPassword("");
        setIsDialogOpen(false);
        fetchAdmins();
      } else {
        const errorData = await res.json();
        toast.error(errorData.detail || "Failed to add admin account.");
      }
    } catch {
      toast.error("An error occurred. Please try again.");
    } finally {
      setAddingAdmin(false);
    }
  };

  return (
    <div className="flex justify-center py-12 px-4">
      <div className="w-full max-w-2xl space-y-6">
        <div>
          <h1 className="text-2xl font-bold">Platform Settings</h1>
          <p className="text-muted-foreground">
            Manage your platform configuration and integrations.
          </p>
        </div>

        {/* Admins Management Section */}
        <Card className="border border-white/[0.08] bg-zinc-950/40 backdrop-blur-md">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
            <div>
              <CardTitle className="flex items-center gap-2 text-xl">
                <Users className="h-5 w-5 text-violet-400" />
                Admin Accounts
              </CardTitle>
              <CardDescription>
                Manage the administrators who can access this AZS Solution&apos;s AI agent console.
              </CardDescription>
            </div>
            <Button
              size="sm"
              onClick={() => setIsDialogOpen(true)}
              className="bg-violet-600 hover:bg-violet-500 text-white gap-1.5 cursor-pointer shadow-[0_0_15px_rgba(124,58,237,0.2)]"
            >
              <UserPlus className="h-4 w-4" />
              Add Admin
            </Button>
          </CardHeader>
          <CardContent>
            {loadingAdmins ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin text-violet-500" />
              </div>
            ) : (
              <div className="rounded-md border border-white/[0.06] overflow-hidden">
                <Table>
                  <TableHeader className="bg-white/[0.02]">
                    <TableRow className="border-white/[0.06]">
                      <TableHead className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">ID</TableHead>
                      <TableHead className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">Email Address</TableHead>
                      <TableHead className="text-xs font-semibold text-zinc-400 uppercase tracking-wider text-right">Role</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {admins.map((admin) => (
                      <TableRow key={admin.id} className="border-white/[0.06] hover:bg-white/[0.01] transition-colors">
                        <TableCell className="font-mono text-zinc-500 text-xs">{admin.id}</TableCell>
                        <TableCell className="font-medium text-zinc-200">{admin.email}</TableCell>
                        <TableCell className="text-right">
                          <span className="inline-flex items-center gap-1 text-xs font-semibold text-violet-400 bg-violet-500/10 px-2.5 py-0.5 rounded-full">
                            <Shield className="h-3.5 w-3.5" />
                            Administrator
                          </span>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Add Admin Dialog */}
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogContent className="sm:max-w-md border-white/[0.08] bg-zinc-950 text-white">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2 text-xl font-bold">
                <UserPlus className="h-5 w-5 text-violet-400" />
                Add Admin Account
              </DialogTitle>
              <DialogDescription className="text-zinc-400">
                Create a new database-backed administrator account.
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleAddAdmin} className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="new-email" className="text-xs font-semibold uppercase tracking-wider text-zinc-400 flex items-center gap-1.5">
                  <Mail className="h-3.5 w-3.5" />
                  Email Address
                </Label>
                <Input
                  id="new-email"
                  type="email"
                  placeholder="admin-partner@azs-solution.ai"
                  value={newEmail}
                  onChange={(e) => setNewEmail(e.target.value)}
                  required
                  className="bg-white/[0.04] border-white/[0.08] text-white placeholder-zinc-500 focus:bg-white/[0.06] focus:border-violet-500/50 focus:ring-violet-500/20 transition-all rounded-lg h-11"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="new-password" className="text-xs font-semibold uppercase tracking-wider text-zinc-400 flex items-center gap-1.5">
                  <KeyRound className="h-3.5 w-3.5" />
                  Password
                </Label>
                <Input
                  id="new-password"
                  type="password"
                  placeholder="At least 8 characters"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                  minLength={8}
                  className="bg-white/[0.04] border-white/[0.08] text-white placeholder-zinc-500 focus:bg-white/[0.06] focus:border-violet-500/50 focus:ring-violet-500/20 transition-all rounded-lg h-11"
                />
              </div>
              <DialogFooter className="pt-4 gap-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setIsDialogOpen(false)}
                  className="border-white/[0.08] hover:bg-white/[0.04] text-white rounded-lg h-11 cursor-pointer"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={addingAdmin}
                  className="bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-500 hover:to-fuchsia-500 text-white font-semibold rounded-lg h-11 cursor-pointer shadow-[0_0_15px_rgba(124,58,237,0.25)]"
                >
                  {addingAdmin ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin mr-1.5" />
                      Creating...
                    </>
                  ) : (
                    "Create Account"
                  )}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>


        <Card>
          <CardHeader>
            <CardTitle>Telemetry</CardTitle>
            <CardDescription>
              Configure Langfuse tracing for your voice agent calls.{" "}
              <a
                href="https://docs.dograh.com/configurations/tracing"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-0.5 underline"
              >
                Learn more <ExternalLink className="h-3 w-3" />
              </a>
            </CardDescription>
          </CardHeader>
          <CardContent>
            <TelemetrySection />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
