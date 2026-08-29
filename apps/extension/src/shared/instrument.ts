export type Instrument = {
  instrumentId: string;
  symbol: string;
  exchange: "NSE" | "BSE";
  name: string;
};

export type PlatformInstrumentReference = {
  platform: "groww";
  platformSymbol: string;
};

export type ResolvedInstrument = {
  instrument: Instrument;
  platformReference: PlatformInstrumentReference;
};
