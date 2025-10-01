
import React from "react";
import ListPage from "./pages/list-page";
import DetailPage from "./pages/detail-page";

/**
 * App shell (presentational):
 * - Show header and a simple nav.
 * - Demonstrates mounting of ListPage and DetailPage.
 *
 * Integration note:
 * Replace the simple render logic with your router (react-router, etc.).
 */

const App: React.FC = () => {
  // Placeholder view selector for demo purposes.
  // Host apps should replace this with their router.
  const [view] = React.useState<"list" | "detail">("list");

  return (
    <div>
      <header className="app-header">
        <div className="container" style={{display:"flex", alignItems:"center", gap:16}}>
          <div className="app-title">Prototype UI</div>
          <nav style={{marginLeft:"auto"}}>
            <a href="#" style={{marginRight:12}}>Home</a>
            <a href="#/items">Items</a>
          </nav>
        </div>
      </header>

      <main className="container" style={{paddingTop:16}}>
        {/* Router placeholder:
            Replace the below conditional with your Router (react-router Routes)
            e.g. <Routes><Route path="/" element={<ListPage/>} />...</Routes>
        */}
        {view === "list" ? <ListPage /> : <DetailPage id="example-1" />}
      </main>
    </div>
  );
};

export default App;
