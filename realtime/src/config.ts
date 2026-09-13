import "dotenv/config";

export const config = {
  port: parseInt(process.env.PORT || "3001", 10),
  jwtSecret: process.env.JWT_SECRET || "",
  internalApiKey: process.env.INTERNAL_API_KEY || "",
  aiServiceUrl: process.env.AI_SERVICE_URL || "http://127.0.0.1:8000",
  aiTimeoutMs: parseInt(process.env.AI_TIMEOUT_MS || "90000", 10),
  rateLimitPerMin: parseInt(process.env.RATE_LIMIT_PER_MIN || "10", 10),
  databaseUrl:
    process.env.DATABASE_URL ||
    "postgresql://postgres:12345678@localhost:5432/ai_grammar_tutor",
};
