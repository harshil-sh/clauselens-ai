import type { ReactNode } from "react";

type BadgeTone = "neutral" | "accent" | "warning";

type Props = {
  children: ReactNode;
  tone?: BadgeTone;
};

export function Badge({ children, tone = "neutral" }: Props) {
  return (
    <span className="ui-badge" data-tone={tone}>
      {children}
    </span>
  );
}
