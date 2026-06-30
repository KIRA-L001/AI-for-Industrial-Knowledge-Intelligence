import { describe, expect, it } from "vitest";

import { ApiError } from "@/lib/api";
import { cn } from "@/lib/utils";

describe("cn", () => {
  it("merges class names and resolves Tailwind conflicts", () => {
    expect(cn("px-2", "px-4")).toBe("px-4");
    expect(cn("text-sm", false && "hidden", "font-bold")).toBe("text-sm font-bold");
  });
});

describe("ApiError", () => {
  it("carries status, code, and message", () => {
    const err = new ApiError(404, { code: "not_found", message: "missing" });
    expect(err.status).toBe(404);
    expect(err.code).toBe("not_found");
    expect(err.message).toBe("missing");
    expect(err).toBeInstanceOf(Error);
  });
});
