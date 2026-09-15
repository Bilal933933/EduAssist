/** أخطاء السوكت بنفس أكواد بايثون: emit("error", { code, message, requestId }) */
import { ArgumentsHost, Catch } from "@nestjs/common";
import { Socket } from "socket.io";
import { AppError, messageFor } from "../errors";
import { getLogger } from "../logger";
import { getRequestId } from "../request-context";

@Catch()
export class WsExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost) {
    const client = host.switchToWs().getClient<Socket>();
    const rid = getRequestId();
    if (exception instanceof AppError) {
      const { message } = messageFor(exception.code);
      client.emit("error", { code: exception.code, message, requestId: rid });
      return;
    }
    const msg = (exception as Error)?.message ?? "";
    const code = msg.includes("AI_UNREACHABLE") ? "AI_UNREACHABLE" : "INTERNAL_ERROR";
    const { message } = messageFor(code);
    getLogger("errors").error(JSON.stringify({ type: "ws_error", code, error: msg.slice(0, 200) }));
    client.emit("error", { code, message, requestId: rid });
  }
}
