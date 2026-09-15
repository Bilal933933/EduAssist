/** RequestId — يطابق request_id_middleware في backend/app/core/response.py
 * يقرأ X-Request-Id أو يولد 12 hex، يخزنه في AsyncLocalStorage، ويعيده في الرد.
 */
import { Injectable, NestMiddleware } from "@nestjs/common";
import { NextFunction, Request, Response } from "express";
import { newRequestId, runWithRequestId } from "./request-context";

@Injectable()
export class RequestIdMiddleware implements NestMiddleware {
  use(req: Request, res: Response, next: NextFunction) {
    const rid = (req.headers["x-request-id"] as string) || newRequestId();
    (req as unknown as { requestId: string }).requestId = rid;
    res.setHeader("X-Request-Id", rid);
    runWithRequestId(rid, () => next());
  }
}
