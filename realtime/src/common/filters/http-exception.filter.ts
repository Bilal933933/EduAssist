/** هندلة الأخطاء الموحدة — تطابق backend/app/core/exceptions.py
 * AppError → fail(code) | 401 → UNAUTHORIZED | 404 → NOT_FOUND
 * 422/validation → VALIDATION_ERROR | غيره → INTERNAL_ERROR (بلا تسريب detail).
 * تمرير شفاف: خطأ axios يحمل مغلف بايثون {ok:false} يُمرر كما هو.
 */
import { ArgumentsHost, Catch, ExceptionFilter, HttpException, HttpStatus } from "@nestjs/common";
import { Request, Response } from "express";
import { AppError, messageFor } from "../errors";
import { getLogger } from "../logger";
import { getRequestId } from "../request-context";
import { fail, isEnvelope } from "../response";

@Catch()
export class HttpExceptionFilter implements ExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost) {
    // WS يُعالج بفلتر السوكت — هنا HTTP فقط
    if (host.getType() !== "http") throw exception;
    const ctx = host.switchToHttp();
    const res = ctx.getResponse<Response>();
    const req = ctx.getRequest<Request>();
    const rid = getRequestId() ?? (req.headers["x-request-id"] as string) ?? null;

    // 1) تمرير شفاف لمغلف بايثون عبر البروكسي
    const axiosData = (exception as { response?: { data?: unknown; status?: number } })?.response?.data;
    if (isEnvelope(axiosData)) {
      res.status((exception as { response: { status: number } }).response.status ?? 500).json(axiosData);
      return;
    }

    // 2) خطأ بيزنس معروف
    if (exception instanceof AppError) {
      const { status, message } = messageFor(exception.code);
      getLogger("errors").warn(JSON.stringify({ type: "app_error", code: exception.code, path: req.url }));
      res.status(status).json(fail(exception.code, message, rid));
      return;
    }

    // 3) HttpException من Nest (تشمل ValidationPipe و UnauthorizedException)
    if (exception instanceof HttpException) {
      const status = exception.getStatus();
      let code = "INTERNAL_ERROR";
      if (status === 401) code = "UNAUTHORIZED";
      else if (status === 404) code = "NOT_FOUND";
      else if (status === 422 || status === HttpStatus.BAD_REQUEST) code = "VALIDATION_ERROR";
      const { message } = messageFor(code);
      res.status(status === HttpStatus.BAD_REQUEST ? 422 : status).json(fail(code, message, rid));
      return;
    }

    // 4) أي شيء آخر → INTERNAL_ERROR بلا تسريب
    getLogger("errors").error(
      JSON.stringify({ type: "unhandled", path: req.url, error: String((exception as Error)?.message ?? exception).slice(0, 200) }),
    );
    const { status, message } = messageFor("INTERNAL_ERROR");
    res.status(status).json(fail("INTERNAL_ERROR", message, rid));
  }
}
