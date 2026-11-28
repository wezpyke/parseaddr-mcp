export declare const VERSION: string;

export interface ClientOptions {
  /** Defaults to the PARSEADDR_API_KEY environment variable. */
  apiKey?: string;
  /** Defaults to PARSEADDR_API_BASE, then https://api.parseaddr.com. */
  baseUrl?: string;
  /** Request timeout in milliseconds. Default 15000. */
  timeoutMs?: number;
}

export interface ParseOptions extends ClientOptions {
  /** Optional ISO language hint, e.g. "en". */
  language?: string;
}

export interface Component {
  label: string;
  value: string;
}

export interface ParseResult {
  input: string;
  components: Component[];
  /** Flat map keyed by libpostal label: house_number, road, unit, city, postcode, country, ... */
  parsed: Record<string, string>;
}

export interface ExpandResult {
  input: string;
  variants: string[];
}

export declare class ParseAddrError extends Error {
  status: number;
  detail: unknown;
}

export declare function parse(address: string, options?: ParseOptions): Promise<ParseResult>;
export declare function expand(address: string, options?: ClientOptions): Promise<ExpandResult>;

declare const _default: {
  parse: typeof parse;
  expand: typeof expand;
  ParseAddrError: typeof ParseAddrError;
  VERSION: string;
};
export default _default;
