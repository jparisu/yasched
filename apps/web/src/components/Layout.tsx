import { useState } from "react";
import { Sidebar } from "./Sidebar";
import { Dashboard } from "./pages/Dashboard";

type Page = "dashboard";

function renderPage(page: Page) {
  switch (page) {
    case "dashboard":
      return <Dashboard />;
  }
}

export function Layout() {
  const [currentPage, setCurrentPage] = useState<Page>("dashboard");

  return (
    <div className="flex h-screen bg-background">
      <div className="flex-shrink-0">
        <Sidebar currentPage={currentPage} onPageChange={(p) => setCurrentPage(p as Page)} />
      </div>
      <main className="flex-1 overflow-auto">{renderPage(currentPage)}</main>
    </div>
  );
}
