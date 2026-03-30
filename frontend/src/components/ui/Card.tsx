import type { HTMLAttributes, ReactNode } from "react";

type Props = HTMLAttributes<HTMLElement> & {
  children: ReactNode;
};

export function Card({ children, className, ...props }: Props) {
  const classes = className ? `ui-card ${className}` : "ui-card";

  return (
    <section {...props} className={classes}>
      {children}
    </section>
  );
}
