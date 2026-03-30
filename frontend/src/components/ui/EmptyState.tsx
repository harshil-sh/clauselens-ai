import type { ReactNode } from "react";
import { Card } from "./Card";

type Props = {
  title: string;
  description: ReactNode;
};

export function EmptyState({ title, description }: Props) {
  return (
    <Card className="ui-empty-state">
      <h2>{title}</h2>
      <p>{description}</p>
    </Card>
  );
}
