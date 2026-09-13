import jwt from "jsonwebtoken";
import { config } from "../config";

export interface TokenPayload {
  sub: number;
  email: string;
}

export function signToken(payload: TokenPayload): string {
  return jwt.sign(payload, config.jwtSecret, { expiresIn: "7d" });
}

export function verifyToken(token: string): TokenPayload | null {
  try {
    return jwt.verify(token, config.jwtSecret) as unknown as TokenPayload;
  } catch {
    return null;
  }
}
