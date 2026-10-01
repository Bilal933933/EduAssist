/** DTOs المصادقة — مزينة بـ class-validator.
 * مطلوبة لأن ValidationPipe العمومي يعمل بـ whitelist:true
 * فيجرد أي خاصية بلا decorator (كان يجعل dto فارغاً دائماً → 422).
 */
import { IsEmail, IsOptional, IsString, MinLength } from "class-validator";

export class RegisterDto {
  @IsEmail()
  email!: string;

  @IsString()
  @MinLength(6)
  password!: string;

  @IsOptional()
  @IsString()
  name?: string;
}

export class LoginDto {
  @IsEmail()
  email!: string;

  @IsString()
  password!: string;
}
