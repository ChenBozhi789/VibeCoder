
import React from "react";
import Badge from "../atoms/badge";

export interface CardItem {
  id: string;
  title: string;
  subtitle?: string;
  description?: string;
  badges?: string[];
}

export interface CardProps {
  item: CardItem;
  onSelect?: (id: string) => void;
}

const Card: React.FC<CardProps> = ({ item, onSelect }) => {
  return (
    <article className="card" tabIndex={0} aria-labelledby={`card-title-${item.id}`} role="article" onClick={() => onSelect && onSelect(item.id)} onKeyDown={(e) => { if (e.key === "Enter") onSelect && onSelect(item.id) }}>
      <div style={{display:"flex", justifyContent:"space-between", alignItems:"center"}}>
        <div>
          <div id={`card-title-${item.id}`} className="card-title">{item.title}</div>
          {item.subtitle && <div className="card-sub">{item.subtitle}</div>}
        </div>
        <div style={{display:"flex", gap:8}}>
          {item.badges && item.badges.map((b, i) => <Badge key={i}>{b}</Badge>)}
        </div>
      </div>
      {item.description && <p style={{marginTop:8,color:"#475569"}}>{item.description}</p>}
    </article>
  );
};

export default Card;
