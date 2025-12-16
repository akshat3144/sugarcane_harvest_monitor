import { Calendar } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card } from "@/components/ui/card";

interface DateFilterProps {
  selectedMonth: string;
  selectedYear: string;
  onMonthChange: (month: string) => void;
  onYearChange: (year: string) => void;
}

const MONTHS = [
  { value: "all", label: "All Months" },
  { value: "1", label: "January" },
  { value: "2", label: "February" },
  { value: "3", label: "March" },
  { value: "4", label: "April" },
  { value: "5", label: "May" },
  { value: "6", label: "June" },
  { value: "7", label: "July" },
  { value: "8", label: "August" },
  { value: "9", label: "September" },
  { value: "10", label: "October" },
  { value: "11", label: "November" },
  { value: "12", label: "December" },
];

// Generate years from current year - 1 to current year + 1
const currentYear = new Date().getFullYear();
const YEARS = [
  { value: "all", label: "All Years" },
  ...Array.from({ length: 3 }, (_, i) => {
    const year = (currentYear - 1 + i).toString();
    return { value: year, label: year };
  }),
];

export const DateFilter = ({
  selectedMonth,
  selectedYear,
  onMonthChange,
  onYearChange,
}: DateFilterProps) => {
  return (
    <Card className="p-4 bg-dashboard-card border-dashboard-border">
      <div className="flex items-center gap-4 flex-wrap">
        <div className="flex items-center gap-2">
          <Calendar className="h-5 w-5 text-primary" />
          <span className="text-sm font-medium text-white">
            Filter by Survey Date:
          </span>
        </div>

        <div className="flex gap-3">
          <div className="w-40">
            <Select value={selectedMonth} onValueChange={onMonthChange}>
              <SelectTrigger className="bg-background/50 border-dashboard-border text-white">
                <SelectValue placeholder="Select month" />
              </SelectTrigger>
              <SelectContent className="z-[9999] bg-dashboard-card border-dashboard-border">
                {MONTHS.map((month) => (
                  <SelectItem
                    key={month.value}
                    value={month.value}
                    className="text-white hover:bg-background/50"
                  >
                    {month.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="w-32">
            <Select value={selectedYear} onValueChange={onYearChange}>
              <SelectTrigger className="bg-background/50 border-dashboard-border text-white">
                <SelectValue placeholder="Select year" />
              </SelectTrigger>
              <SelectContent className="z-[9999] bg-dashboard-card border-dashboard-border">
                {YEARS.map((year) => (
                  <SelectItem
                    key={year.value}
                    value={year.value}
                    className="text-white hover:bg-background/50"
                  >
                    {year.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>
    </Card>
  );
};
