
import React from "react";
import { CardItem } from "../molecules/card";

export interface DetailViewProps {
  item?: CardItem | null;
  isLoading?: boolean;
  error?: string | null;
}

const DetailView: React.FC<DetailViewProps> = ({ item, isLoading=false, error=null }) => {
  if (isLoading) return <div aria-busy="true" className="card">Loading...</div>;
  if (error) return <div role="alert" style={{padding:16, background:"#fff1f2", borderRadius:8}}>{error}</div>;
  if (!item) return <div className="empty-state">Item not found.</div>;

  return (
    <article className="card" aria-labelledby={`detail-title-${item.id}`}>
      <h2 id={`detail-title-${item.id}`} style={{marginTop:0}}>{item.title}</h2>
      {item.subtitle && <div style={{color:"#6b7280", marginBottom:8}}>{item.subtitle}</div>}
      {item.badges && <div style={{display:"flex",gap:8,marginBottom:8}}>{item.badges.map((b,i)=><span key={i} style={{background:"#eef2ff",padding:"2px 8px",borderRadius:999}}>{b}</span>)}</div>}
      <p style={{color:"#475569"}}>{item.description}</p>
    </article>
  );
};

export default DetailView;
