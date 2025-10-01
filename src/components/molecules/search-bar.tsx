
import React from "react";
import TextInput from "../atoms/input";
import Button from "../atoms/button";

export interface SearchBarProps {
  query?: string;
  onQueryChange?: (q: string) => void;
  onSearch?: () => void;
  placeholder?: string;
}

const SearchBar: React.FC<SearchBarProps> = ({ query="", onQueryChange, onSearch, placeholder="Search..." }) => {
  return (
    <div className="search-row" role="search" aria-label="Search items">
      <TextInput value={query} onChange={onQueryChange} placeholder={placeholder} ariaLabel={placeholder} />
      <Button label="Search" onClick={onSearch} />
    </div>
  );
};

export default SearchBar;
