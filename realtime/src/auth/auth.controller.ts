import {
  BadRequestException,
  Body,
  ConflictException,
  Controller,
  HttpCode,
  Post,
  UnauthorizedException,
} from "@nestjs/common";
import { createUser, findUserByEmail } from "../db";
import { hashPassword, verifyPassword } from "./password.util";
import { signToken } from "./jwt.util";

class RegisterDto {
  email!: string;
  password!: string;
  name?: string;
}

class LoginDto {
  email!: string;
  password!: string;
}

@Controller("auth")
export class AuthController {
  @Post("register")
  @HttpCode(201)
  async register(@Body() dto: RegisterDto) {
    const email = (dto.email || "").trim().toLowerCase();
    if (!email.includes("@") || !dto.password || dto.password.length < 6) {
      throw new BadRequestException(
        "بريد إلكتروني غير صالح أو كلمة مرور أقصر من 6 أحرف.",
      );
    }
    const existing = await findUserByEmail(email);
    if (existing) {
      throw new ConflictException("البريد الإلكتروني مسجل بالفعل.");
    }
    const user = await createUser(email, dto.name?.trim() || null, hashPassword(dto.password));
    return {
      token: signToken({ sub: user.id, email: user.email }),
      user: { id: user.id, email: user.email, name: user.name },
    };
  }

  @Post("login")
  async login(@Body() dto: LoginDto) {
    const email = (dto.email || "").trim().toLowerCase();
    const user = await findUserByEmail(email);
    if (!user || !verifyPassword(dto.password || "", user.password_hash)) {
      throw new UnauthorizedException("بيانات الدخول غير صحيحة.");
    }
    return {
      token: signToken({ sub: user.id, email: user.email }),
      user: { id: user.id, email: user.email, name: user.name },
    };
  }
}
