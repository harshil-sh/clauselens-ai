import type { ButtonHTMLAttributes, ReactNode } from "react";

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  children: ReactNode;
};

export function Button({ children, className, type = "button", ...props }: Props) {
  const classes = className ? `ui-button ${className}` : "ui-button";

  return (
    <button {...props} type={type} className={classes}>
      {children}
    </button>
  );
}
