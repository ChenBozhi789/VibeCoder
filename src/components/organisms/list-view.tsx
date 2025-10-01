
import React from "react";
import Card, { CardItem } from "../molecules/card";

export interface ListViewProps {
  items: CardItem[];
  isLoading?: boolean;
  error?: string | null;
  onSelect?: (id: string) => void;
  emptyMessage?: string;
}

const LoadingSkeleton: React.FC = () => (
  <div>
    <div className="card" aria-busy="true" style={{height:80}}></div>
    <div className="card" aria-busy="true" style={{height:80}}></div>
    <div className="card" aria-busy="true" style={{height:80}}></div>
  </div>
);

const ListView: React.FC<ListViewProps> = ({ items, isLoading=false, error=null, onSelect, emptyMessage="No items found." }) => {
  if (isLoading) return <LoadingSkeleton />;

  if (error) return (
    <div role="alert" style={{padding:16, background:"#fff1f2", borderRadius:8}}>
      <strong>Error</strong>
      <div style={{color:"#7f1d1d"}}>{error}</div>
    </div>
  );

  if (!items || items.length === 0) {
    return <div className="empty-state" role="status">{emptyMessage}</div>;
  }

  return (
    <div>
      {items.map((it) => <Card item={it} key={it.id} onSelect={onSelect} />)}
    </div>
  );
};

export default ListView;
