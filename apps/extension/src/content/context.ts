import type { StockIdentity } from "./platforms/groww";
import type { ResolvedInstrument } from "../shared/instrument";

export type StockPageContext = StockIdentity & {
  instrument: ResolvedInstrument | null;

  price: number | null;
  change: number | null;
  changePercent: number | null;

  url: string;
  capturedAt: string;
};
