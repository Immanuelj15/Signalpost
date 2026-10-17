import { createBrowserRouter } from "react-router-dom";
import { AppShell } from "../components/layout/AppShell";
import { OverviewPage } from "../pages/OverviewPage";
import { CompaniesPage } from "../pages/CompaniesPage";
import { CompanyProfilePage } from "../pages/CompanyProfilePage";
import { ResearchPage } from "../pages/ResearchPage";
import { ChangesPage } from "../pages/ChangesPage";
import { SourcesPage } from "../pages/SourcesPage";
import { SettingsPage } from "../pages/SettingsPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppShell />,
    children: [
      {
        index: true,
        element: <OverviewPage />,
      },
      {
        path: "companies",
        element: <CompaniesPage />,
      },
      {
        path: "companies/:orgNumber",
        element: <CompanyProfilePage />,
      },
      {
        path: "research",
        element: <ResearchPage />,
      },
      {
        path: "changes",
        element: <ChangesPage />,
      },
      {
        path: "sources",
        element: <SourcesPage />,
      },
      {
        path: "settings",
        element: <SettingsPage />,
      },
    ],
  },
]);
