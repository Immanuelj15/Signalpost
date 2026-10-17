import { CompanyProfile } from "../types";

export const exportService = {
  exportCompaniesToJson(companies: CompanyProfile[], filename = "signalpost_companies.json") {
    const jsonStr = JSON.stringify(companies, null, 2);
    const blob = new Blob([jsonStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  },

  exportCompaniesToCsv(companies: CompanyProfile[], filename = "signalpost_companies.csv") {
    const headers = [
      "Organization Number",
      "Official Name",
      "Status",
      "Organization Type",
      "Industry Code",
      "Industry Description",
      "Postal Code",
      "City",
      "Employees",
      "Website",
      "Verified Facts Count",
      "Identity Status",
      "Research Status",
      "Last Researched At",
    ];

    const rows = companies.map((c) => {
      const primaryIndustry = c.company.industry_codes?.[0];
      return [
        `"${c.organization_number}"`,
        `"${(c.company.official_name || "").replace(/"/g, '""')}"`,
        `"${c.company.status || ""}"`,
        `"${c.company.organization_type || ""}"`,
        `"${primaryIndustry?.code || ""}"`,
        `"${(primaryIndustry?.description || "").replace(/"/g, '""')}"`,
        `"${c.company.business_address?.postal_code || ""}"`,
        `"${c.company.business_address?.city || ""}"`,
        c.company.employees !== undefined ? c.company.employees : "",
        `"${c.company.website || ""}"`,
        c.facts?.length || 0,
        `"${c.identity_status}"`,
        `"${c.research_status}"`,
        `"${c.last_researched_at || ""}"`,
      ].join(",");
    });

    const csvContent = [headers.join(","), ...rows].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  },
};
