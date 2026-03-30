import type { ReactNode } from "react";
import { Card } from "./Card";

type Props = {
  title: string;
  description: ReactNode;
  tone?: "default" | "loading" | "error";
  action?: ReactNode;
};

export function EmptyState({ title, description, tone = "default", action }: Props) {
  return (
    <Card className="ui-empty-state" data-tone={tone}>
      {tone === "loading" ? <span className="ui-empty-state__indicator" aria-hidden="true" /> : null}
      <h2>{title}</h2>
      <p>{description}</p>
      {action ? <div className="ui-empty-state__action">{action}</div> : null}
    </Card>
  );
}
