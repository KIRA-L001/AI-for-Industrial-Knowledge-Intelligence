"use client";

import { UploadCloud } from "lucide-react";
import { useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { Table, TBody, TD, TH, THead, TR } from "@/components/ui/table";
import { ApiError } from "@/lib/api";
import { useDocuments, useUploadDocument } from "@/lib/hooks/use-documents";

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

const STATUS_STYLES: Record<string, string> = {
  uploaded: "bg-blue-500/15 text-blue-500",
  ready: "bg-green-500/15 text-green-500",
  failed: "bg-destructive/15 text-destructive",
};

export default function DocumentsPage() {
  const { data, isLoading } = useDocuments();
  const upload = useUploadDocument();
  const inputRef = useRef<HTMLInputElement>(null);
  const [error, setError] = useState<string | null>(null);

  async function onFiles(files: FileList | null) {
    if (!files?.length) return;
    setError(null);
    try {
      for (const file of Array.from(files)) {
        await upload.mutateAsync(file);
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Upload failed");
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Documents</h1>
        <p className="text-sm text-muted-foreground">
          Upload PDF, DOCX, XLSX, CSV, or images. Processing status is tracked per document.
        </p>
      </div>

      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        className="flex w-full flex-col items-center gap-2 rounded-xl border-2 border-dashed border-border bg-card p-10 text-center transition hover:border-primary/50"
      >
        <UploadCloud className="h-8 w-8 text-muted-foreground" />
        <span className="font-medium">Click to upload</span>
        <span className="text-sm text-muted-foreground">
          {upload.isPending ? "Uploading…" : "PDF, DOCX, XLSX, CSV, PNG, JPG, TIFF (max 50 MB)"}
        </span>
      </button>
      <input
        ref={inputRef}
        type="file"
        multiple
        className="hidden"
        accept=".pdf,.docx,.xlsx,.csv,.png,.jpg,.jpeg,.tiff"
        onChange={(e) => onFiles(e.target.files)}
      />
      {error && <p className="text-sm text-destructive">{error}</p>}

      {isLoading ? (
        <p className="text-sm text-muted-foreground">Loading…</p>
      ) : (
        <Table>
          <THead>
            <TR>
              <TH>Filename</TH>
              <TH>Size</TH>
              <TH>Status</TH>
              <TH>Uploaded</TH>
            </TR>
          </THead>
          <TBody>
            {(data?.items ?? []).map((d) => (
              <TR key={d.id}>
                <TD className="font-medium">{d.filename}</TD>
                <TD>{formatBytes(d.size_bytes)}</TD>
                <TD>
                  <span
                    className={`rounded-full px-2 py-0.5 text-xs capitalize ${
                      STATUS_STYLES[d.status] ?? "bg-muted text-muted-foreground"
                    }`}
                  >
                    {d.status}
                  </span>
                </TD>
                <TD>{new Date(d.created_at).toLocaleString()}</TD>
              </TR>
            ))}
            {data?.items.length === 0 && (
              <TR>
                <TD className="text-muted-foreground" colSpan={4}>
                  No documents yet.
                </TD>
              </TR>
            )}
          </TBody>
        </Table>
      )}
    </div>
  );
}
