import {
  ExceptionFilter,
  Catch,
  ArgumentsHost,
  HttpException,
  HttpStatus,
  Logger,
} from '@nestjs/common';
import { Response, Request } from 'express';

/**
 * GlobalExceptionFilter - معالج الأخطاء الموحد
 * يتعامل مع جميع الأخطاء في التطبيق ويعيدها بصيغة موحدة
 */

interface ErrorResponse {
  statusCode: number;
  errorCode: string;
  message: string;
  timestamp: string;
  path: string;
  details?: any;
}

@Catch()
export class GlobalExceptionFilter implements ExceptionFilter {
  private readonly logger = new Logger('ExceptionFilter');

  catch(exception: unknown, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();
    const request = ctx.getRequest<Request>();

    let errorResponse: ErrorResponse = {
      statusCode: HttpStatus.INTERNAL_SERVER_ERROR,
      errorCode: 'INTERNAL_SERVER_ERROR',
      message: 'حدث خطأ غير متوقع',
      timestamp: new Date().toISOString(),
      path: request.url,
    };

    // معالجة HttpException
    if (exception instanceof HttpException) {
      const status = exception.getStatus();
      const exceptionResponse = exception.getResponse();

      errorResponse.statusCode = status;
      errorResponse.timestamp = new Date().toISOString();

      if (typeof exceptionResponse === 'object') {
        const errorObj = exceptionResponse as any;
        errorResponse.message = errorObj.message || 'حدث خطأ';
        errorResponse.details = errorObj;

        // تحديد رمز الخطأ بناءً على status code
        switch (status) {
          case HttpStatus.BAD_REQUEST:
            errorResponse.errorCode = 'BAD_REQUEST';
            break;
          case HttpStatus.UNAUTHORIZED:
            errorResponse.errorCode = 'UNAUTHORIZED';
            break;
          case HttpStatus.FORBIDDEN:
            errorResponse.errorCode = 'FORBIDDEN';
            break;
          case HttpStatus.NOT_FOUND:
            errorResponse.errorCode = 'NOT_FOUND';
            break;
          case HttpStatus.CONFLICT:
            errorResponse.errorCode = 'CONFLICT';
            break;
          default:
            errorResponse.errorCode = 'HTTP_ERROR';
        }
      } else {
        errorResponse.message = exceptionResponse.toString();
        errorResponse.errorCode = 'HTTP_ERROR';
      }
    }
    // معالجة الأخطاء الأخرى
    else if (exception instanceof Error) {
      errorResponse.message = exception.message;
      errorResponse.errorCode = exception.name || 'ERROR';

      // تسجيل Stack Trace للأخطاء الحقيقية
      if (process.env.NODE_ENV === 'development') {
        errorResponse.details = {
          stack: exception.stack,
          name: exception.name,
        };
      }
    }

    // تسجيل الخطأ
    this.logger.error(
      `Error: ${errorResponse.errorCode} - ${errorResponse.message}`,
      exception instanceof Error ? exception.stack : undefined
    );

    // إرسال الاستجابة
    response.status(errorResponse.statusCode).json(errorResponse);
  }
}
