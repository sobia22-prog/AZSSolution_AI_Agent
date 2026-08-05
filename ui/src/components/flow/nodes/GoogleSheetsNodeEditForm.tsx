import { AlertCircle, CheckCircle2, Database, FileSpreadsheet, Loader2, RefreshCw, Table } from "lucide-react";
import React, { useCallback, useEffect, useMemo, useState } from "react";

import type { ToolResponse } from "@/client/types.gen";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { useAuth } from "@/lib/auth";

export interface GoogleSheetsNodeEditFormProps {
  values: Record<string, unknown>;
  onChange: (next: Record<string, unknown>) => void;
  tools?: ToolResponse[];
}

export function GoogleSheetsNodeEditForm({
  values,
  onChange,
  tools = [],
}: GoogleSheetsNodeEditFormProps) {
  const { getAccessToken } = useAuth();

  const [accounts, setAccounts] = useState<Array<{ uuid: string; name: string }>>([]);
  const [files, setFiles] = useState<Array<{ id: string; name: string; webViewLink?: string }>>([]);
  const [tabs, setTabs] = useState<string[]>([]);

  const [loadingAccounts, setLoadingAccounts] = useState(false);
  const [loadingFiles, setLoadingFiles] = useState(false);
  const [loadingTabs, setLoadingTabs] = useState(false);
  const [loadingColumns, setLoadingColumns] = useState(false);
  const [connectingAuth, setConnectingAuth] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);

  const credentialUuid = (values.credential_uuid as string) || "";
  const spreadsheetIdOrUrl = (values.spreadsheet_id_or_url as string) || "";
  const sheetName = (values.sheet_name as string) || "Sheet1";

  const rawMappings = (values.column_mappings as Array<{ column_name: string; value_template: string }>) || [];
  const columnMappings = useMemo(() => rawMappings, [JSON.stringify(rawMappings)]); // eslint-disable-line react-hooks/exhaustive-deps

  const updateField = useCallback(
    (field: string, val: unknown) => {
      onChange({ ...values, [field]: val });
    },
    [values, onChange]
  );

  // Helper to build headers with Bearer token
  const getAuthHeaders = useCallback(async (): Promise<Record<string, string>> => {
    try {
      const token = await getAccessToken();
      const headers: Record<string, string> = {};
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }
      return headers;
    } catch {
      return {};
    }
  }, [getAccessToken]);

  // Fetch mounted Google accounts
  const fetchAccounts = useCallback(async () => {
    setLoadingAccounts(true);
    try {
      const headers = await getAuthHeaders();
      const res = await fetch("/api/v1/integrations/google-drive/accounts", { headers });
      if (res.ok) {
        const data = await res.json();
        setAccounts(data || []);
        if (data.length > 0 && !credentialUuid) {
          updateField("credential_uuid", data[0].uuid);
        }
      }
    } catch (err) {
      console.error("Failed to fetch Google Drive accounts:", err);
    } finally {
      setLoadingAccounts(false);
    }
  }, [credentialUuid, getAuthHeaders, updateField]);

  useEffect(() => {
    fetchAccounts();
  }, [fetchAccounts]);

  // Fetch files when credential_uuid changes
  const fetchFiles = useCallback(async (credUuid: string) => {
    if (!credUuid) return;
    setLoadingFiles(true);
    try {
      const headers = await getAuthHeaders();
      const res = await fetch(`/api/v1/integrations/google-drive/files?credential_uuid=${credUuid}`, { headers });
      if (res.ok) {
        const data = await res.json();
        setFiles(data.files || []);
      }
    } catch (err) {
      console.error("Failed to fetch Google Drive files:", err);
    } finally {
      setLoadingFiles(false);
    }
  }, [getAuthHeaders]);

  useEffect(() => {
    if (credentialUuid) {
      fetchFiles(credentialUuid);
    }
  }, [credentialUuid, fetchFiles]);

  // Fetch worksheet tabs when spreadsheet changes
  const fetchTabs = useCallback(async (credUuid: string, sheetId: string) => {
    if (!credUuid || !sheetId) return;
    setLoadingTabs(true);
    try {
      const headers = await getAuthHeaders();
      const res = await fetch(`/api/v1/integrations/google-drive/sheets?credential_uuid=${credUuid}&spreadsheet_id=${encodeURIComponent(sheetId)}`, { headers });
      if (res.ok) {
        const data = await res.json();
        setTabs(data.sheets || ["Sheet1"]);
      }
    } catch (err) {
      console.error("Failed to fetch tabs:", err);
    } finally {
      setLoadingTabs(false);
    }
  }, [getAuthHeaders]);

  useEffect(() => {
    if (credentialUuid && spreadsheetIdOrUrl) {
      fetchTabs(credentialUuid, spreadsheetIdOrUrl);
    }
  }, [credentialUuid, spreadsheetIdOrUrl, fetchTabs]);

  // Fetch header columns when sheet_name changes
  const fetchColumns = useCallback(async (credUuid: string, sheetId: string, tab: string) => {
    if (!credUuid || !sheetId) return;
    setLoadingColumns(true);
    try {
      const headers = await getAuthHeaders();
      const res = await fetch(`/api/v1/integrations/google-drive/columns?credential_uuid=${credUuid}&spreadsheet_id=${encodeURIComponent(sheetId)}&sheet_name=${encodeURIComponent(tab)}`, { headers });
      if (res.ok) {
        const data = await res.json();
        const cols: string[] = data.columns || [];

        if (cols.length > 0) {
          const currentMap = new Map(columnMappings.map(c => [c.column_name, c.value_template]));
          const newMappings = cols.map((col: string) => {
            if (currentMap.has(col)) {
              return { column_name: col, value_template: currentMap.get(col)! };
            }
            const normalized = col.toLowerCase();
            let template = `{{gathered_context.${col.toLowerCase().replace(/\s+/g, "_")}}}`;
            if (normalized.includes("time") || normalized.includes("date")) template = "{{call_time}}";
            else if (normalized.includes("phone")) template = "{{initial_context.phone_number}}";
            else if (normalized.includes("recording")) template = "{{recording_url}}";
            else if (normalized.includes("transcript")) template = "{{transcript_url}}";
            else if (normalized.includes("summary")) template = "{{gathered_context.summary}}";
            else if (normalized.includes("disposition")) template = "{{gathered_context.call_disposition}}";
            else if (normalized.includes("duration")) template = "{{cost_info.call_duration_seconds}}";

            return { column_name: col, value_template: template };
          });
          updateField("column_mappings", newMappings);
        }
      }
    } catch (err) {
      console.error("Failed to fetch columns:", err);
    } finally {
      setLoadingColumns(false);
    }
  }, [columnMappings, getAuthHeaders, updateField]);

  // Handle 1-Click Google OAuth popup
  const handleConnectDrive = async () => {
    setConnectingAuth(true);
    setAuthError(null);
    try {
      const headers = await getAuthHeaders();
      const redirectUri = `${window.location.origin}/api/v1/integrations/google-drive/callback`;
      const res = await fetch(`/api/v1/integrations/google-drive/auth-url?redirect_uri=${encodeURIComponent(redirectUri)}`, { headers });
      if (res.ok) {
        const data = await res.json();
        const popup = window.open(data.auth_url, "ConnectGoogleDrive", "width=550,height=650");
        const timer = setInterval(() => {
          if (popup?.closed) {
            clearInterval(timer);
            setConnectingAuth(false);
            fetchAccounts();
          }
        }, 1000);
      } else {
        const errData = await res.json().catch(() => ({}));
        setAuthError(errData.detail || "Google OAuth Client ID is not configured on the server. Set GOOGLE_CLIENT_ID environment variable in Railway.");
        setConnectingAuth(false);
      }
    } catch (err) {
      console.error("Failed to start Google Drive auth:", err);
      setAuthError("Failed to connect to Google Drive authorization endpoint.");
      setConnectingAuth(false);
    }
  };

  const handleMappingChange = (colName: string, templateVal: string) => {
    const updated = columnMappings.map(m => m.column_name === colName ? { ...m, value_template: templateVal } : m);
    updateField("column_mappings", updated);
  };

  // Build variable options combining built-ins and user tools
  const availableVariables = useMemo(() => {
    const vars = [
      { label: "Call Timestamp", value: "{{call_time}}" },
      { label: "Caller Phone Number", value: "{{initial_context.phone_number}}" },
      { label: "Call Summary", value: "{{gathered_context.summary}}" },
      { label: "Call Disposition", value: "{{gathered_context.call_disposition}}" },
      { label: "Call Duration (sec)", value: "{{cost_info.call_duration_seconds}}" },
      { label: "Audio Recording URL", value: "{{recording_url}}" },
      { label: "Transcript Download URL", value: "{{transcript_url}}" },
      { label: "Extracted: Customer Name", value: "{{gathered_context.customer_name}}" },
      { label: "Extracted: Email Address", value: "{{gathered_context.email}}" },
    ];

    tools.forEach((t) => {
      vars.push({
        label: `Tool (${t.name}): ${t.name}_result`,
        value: `{{gathered_context.${t.name}_result}}`,
      });
    });

    return vars;
  }, [tools]);

  return (
    <div className="space-y-5 py-2">
      {/* Name & Enable Switch */}
      <div className="flex items-center justify-between border-b pb-3">
        <div className="space-y-0.5">
          <Label className="text-base font-semibold">Google Sheets Export</Label>
          <p className="text-xs text-muted-foreground">
            Save post-call summary and tool-extracted lead data to Google Sheets
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Label htmlFor="gs-enable" className="text-xs font-medium">Enabled</Label>
          <Switch
            id="gs-enable"
            checked={values.google_sheets_enabled !== false}
            onCheckedChange={(c) => updateField("google_sheets_enabled", c)}
          />
        </div>
      </div>

      {/* Step 1: Connect Google Drive */}
      <div className="space-y-2 rounded-lg border p-3.5 bg-muted/20">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileSpreadsheet className="h-4 w-4 text-emerald-600" />
            <span className="text-sm font-medium">1. Mount Google Drive</span>
          </div>
          {accounts.length > 0 && (
            <span className="text-xs text-emerald-600 flex items-center gap-1 font-medium">
              <CheckCircle2 className="h-3.5 w-3.5" /> Mounted ({accounts.length})
            </span>
          )}
        </div>

        {authError && (
          <div className="rounded border border-amber-300 bg-amber-50 dark:bg-amber-950/40 p-2.5 text-xs text-amber-800 dark:text-amber-200 flex items-start gap-2">
            <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">Railway Server Setup Required</p>
              <p className="mt-0.5">{authError}</p>
              <p className="mt-1 text-[11px] text-amber-700 dark:text-amber-300">
                Set <code className="bg-amber-200/60 dark:bg-amber-900/60 px-1 rounded">GOOGLE_CLIENT_ID</code> and <code className="bg-amber-200/60 dark:bg-amber-900/60 px-1 rounded">GOOGLE_CLIENT_SECRET</code> in Railway Service Variables.
              </p>
            </div>
          </div>
        )}

        {accounts.length === 0 ? (
          <Button
            type="button"
            className="w-full bg-emerald-600 hover:bg-emerald-700 text-white gap-2 mt-2"
            onClick={handleConnectDrive}
            disabled={connectingAuth}
          >
            {connectingAuth ? <Loader2 className="h-4 w-4 animate-spin" /> : <Database className="h-4 w-4" />}
            Connect / Mount Google Drive
          </Button>
        ) : (
          <div className="grid gap-2 pt-1">
            <Select value={credentialUuid} onValueChange={(val) => updateField("credential_uuid", val)}>
              <SelectTrigger className="w-full">
                <SelectValue placeholder={loadingAccounts ? "Loading accounts..." : "Select Connected Account"} />
              </SelectTrigger>
              <SelectContent>
                {accounts.map((acc) => (
                  <SelectItem key={acc.uuid} value={acc.uuid}>
                    {acc.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}
      </div>

      {/* Step 2: Select Spreadsheet File & Sheet Tab (100% Automated Dropdowns) */}
      <div className="space-y-3 rounded-lg border p-3.5 bg-muted/20">
        <div className="flex items-center gap-2">
          <Table className="h-4 w-4 text-blue-600" />
          <span className="text-sm font-medium">2. Select Spreadsheet & Worksheet Tab</span>
        </div>

        <div className="grid gap-3">
          <div className="space-y-1">
            <Label className="text-xs">Spreadsheet File (from Drive)</Label>
            <Select
              value={spreadsheetIdOrUrl}
              onValueChange={(val) => {
                updateField("spreadsheet_id_or_url", val);
                if (credentialUuid && val) fetchTabs(credentialUuid, val);
              }}
              disabled={!credentialUuid || files.length === 0}
            >
              <SelectTrigger className="w-full">
                <SelectValue
                  placeholder={
                    !credentialUuid
                      ? "Mount Google Drive above to load files..."
                      : loadingFiles
                      ? "Loading files from Google Drive..."
                      : "Select Excel / Google Sheet File"
                  }
                />
              </SelectTrigger>
              <SelectContent>
                {files.map((file) => (
                  <SelectItem key={file.id} value={file.id}>
                    {file.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {spreadsheetIdOrUrl && (
            <div className="space-y-1">
              <Label className="text-xs">Worksheet Tab</Label>
              <Select
                value={sheetName}
                onValueChange={(val) => {
                  updateField("sheet_name", val);
                  if (credentialUuid && spreadsheetIdOrUrl && val) {
                    fetchColumns(credentialUuid, spreadsheetIdOrUrl, val);
                  }
                }}
                disabled={loadingTabs}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder={loadingTabs ? "Loading sheet tabs..." : "Select Sheet Tab"} />
                </SelectTrigger>
                <SelectContent>
                  {tabs.map((tab) => (
                    <SelectItem key={tab} value={tab}>
                      {tab}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}
        </div>
      </div>

      {/* Step 3: Fetch Columns & Map Variables */}
      {spreadsheetIdOrUrl && (
        <div className="space-y-3 rounded-lg border p-3.5 bg-muted/20">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">3. Map Sheet Columns to Extracted Tool Variables</span>
            {credentialUuid && (
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="gap-1 text-xs"
                onClick={() => fetchColumns(credentialUuid, spreadsheetIdOrUrl, sheetName)}
                disabled={loadingColumns}
              >
                {loadingColumns ? <Loader2 className="h-3 w-3 animate-spin" /> : <RefreshCw className="h-3 w-3" />}
                Fetch Sheet Columns
              </Button>
            )}
          </div>

          {columnMappings.length > 0 ? (
            <div className="space-y-2 pt-1">
              {columnMappings.map((mapping, idx) => (
                <div key={idx} className="flex items-center gap-2 bg-background p-2 rounded border">
                  <span className="text-xs font-semibold w-1/3 truncate text-foreground" title={mapping.column_name}>
                    {mapping.column_name}
                  </span>
                  <span className="text-xs text-muted-foreground">➔</span>
                  <Select
                    value={mapping.value_template}
                    onValueChange={(val) => handleMappingChange(mapping.column_name, val)}
                  >
                    <SelectTrigger className="w-2/3 h-8 text-xs">
                      <SelectValue placeholder="Select Variable" />
                    </SelectTrigger>
                    <SelectContent>
                      {availableVariables.map((v) => (
                        <SelectItem key={v.value} value={v.value} className="text-xs">
                          {v.label} ({v.value})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-muted-foreground py-2 text-center">
              Click &quot;Fetch Sheet Columns&quot; above to automatically detect header columns from your Excel file!
            </p>
          )}
        </div>
      )}
    </div>
  );
}
