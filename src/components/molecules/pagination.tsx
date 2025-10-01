
import React from "react";
import Button from "../atoms/button";

export interface PaginationProps {
  page: number;
  pageSize: number;
  total: number;
  onChange: (page: number) => void;
}

const Pagination: React.FC<PaginationProps> = ({ page, pageSize, total, onChange }) => {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  return (
    <div className="pagination" role="navigation" aria-label="Pagination">
      <Button label="Prev" onClick={() => onChange(Math.max(1, page - 1))} disabled={page <= 1} />
      <span aria-live="polite" style={{alignSelf:"center"}}>Page {page} of {totalPages}</span>
      <Button label="Next" onClick={() => onChange(Math.min(totalPages, page + 1))} disabled={page >= totalPages} />
    </div>
  );
};

export default Pagination;
