"use client";

import Link from 'next/link';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '@/lib/auth';

export default function OverviewPage() {
    const { user } = useAuth();

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="max-w-4xl mx-auto">
                {/* Welcome Card */}
                <Card className="mb-8">
                    <CardHeader>
                        <CardTitle className="text-3xl">
                            {user?.displayName
                                ? `Welcome back, ${user.displayName.split(' ')[0]}!`
                                : "Welcome to AZS Solution's AI Agent"}
                        </CardTitle>
                        <CardDescription className="text-lg mt-2">
                            Build and deploy intelligent voice AI workflows — all in one place.
                        </CardDescription>
                    </CardHeader>
                </Card>

                {/* Quick Actions */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Voice Agents</CardTitle>
                            <CardDescription>
                                Create and manage your AI voice agents with the visual workflow editor.
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <Button asChild>
                                <Link href="/workflow">Go to Agents</Link>
                            </Button>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>Model Configuration</CardTitle>
                            <CardDescription>
                                Set up your LLM, TTS, and STT providers to power your agents.
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <Button asChild variant="outline">
                                <Link href="/model-configurations">Configure Models</Link>
                            </Button>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>Telephony</CardTitle>
                            <CardDescription>
                                Connect phone numbers and configure inbound / outbound call routing.
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <Button asChild variant="outline">
                                <Link href="/telephony-configurations">Manage Telephony</Link>
                            </Button>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>Agent Runs</CardTitle>
                            <CardDescription>
                                Monitor live and historical runs, review transcripts, and track usage.
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <Button asChild variant="outline">
                                <Link href="/usage">View Runs</Link>
                            </Button>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}
