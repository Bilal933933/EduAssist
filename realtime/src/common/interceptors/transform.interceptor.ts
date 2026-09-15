/** تغليف النجاح في ok() — يطابق backend/app/core/response.py
 * يتخطى: المغلف الجاهز (بايثون) + الستر يم (SSE) + الردود الفارغة 204.
 */
import { CallHandler, ExecutionContext, Injectable, NestInterceptor } from "@nestjs/common";
import { Response } from "express";
import { Observable, map } from "rxjs";
import { getRequestId } from "../request-context";
import { isEnvelope, ok } from "../response";

@Injectable()
export class TransformInterceptor implements NestInterceptor {
  intercept(context: ExecutionContext, next: CallHandler): Observable<unknown> {
    const ctx = context.switchToHttp();
    const res = ctx.getResponse<Response | undefined>();
    return next.handle().pipe(
      map((data) => {
        if (data === undefined) return data; // 204 No Content
        if (res && (res.getHeader("Content-Type") as string)?.includes("text/event-stream")) return data;
        if (isEnvelope(data)) return data; // بايثون مغلف جاهز
        return ok(data, getRequestId());
      }),
    );
  }
}
