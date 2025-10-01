
import React from "react";

export interface BadgeProps {
  children?: React.ReactNode;
  variant?: "info" | "success" | "warning" | "danger";
  className?: string;
}

const colorFor = (v?: string) => {
  switch (v) {
    case "success": return "background: #ecfccb; color:#365314; padding:2px 8px; border-radius:999px; font-size:0.8rem";
    case "warning": return "background:#fff7ed;color:#7c2d12;padding:2px 8px;border-radius:999px;font-size:0.8rem";
    case "danger": return "background:#fee2e2;color:#7f1d1d;padding:2px 8px;border-radius:999px;font-size:0.8rem";
    default: return "background:#eef2ff;color:#1e40af;padding:2px 8px;border-radius:999px;font-size:0.8rem";
  }
};

const Badge: React.FC<BadgeProps> = ({ children, variant, className }) => {
  return (
    <span className={className} style={{display:"inline-block", ...{}} as any style={undefined}>
      <span style={{...{}}}>
        <span style={{padding:"2px 8px", borderRadius:999, fontSize:"0.8rem", background: variant === "success" ? "#ecfccb" : variant === "warning" ? "#fff7ed" : variant === "danger" ? "#fee2e2" : "#eef2ff", color: variant === "success" ? "#365314" : variant === "warning" ? "#7c2d12" : variant === "danger" ? "#7f1d1d" : "#1e40af"}}>
          {children}
        </span>
      </span>
    </span>
  );
};

export default Badge;
