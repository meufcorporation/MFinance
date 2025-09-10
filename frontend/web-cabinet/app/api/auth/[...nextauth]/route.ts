import NextAuth, { NextAuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import KeycloakProvider from "next-auth/providers/keycloak";

export const authOptions: NextAuthOptions = {
  providers: [
    KeycloakProvider({
      clientId: process.env.KEYCLOAK_CLIENT_ID || "mfinance-web",
      clientSecret: process.env.KEYCLOAK_CLIENT_SECRET || "mfinance-secret-key-2024",
      issuer: process.env.KEYCLOAK_ISSUER || "http://localhost:8080/realms/mfinance",
    }),
    CredentialsProvider({
      name: "credentials",
      credentials: {
        username: { label: "Username", type: "text" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        if (!credentials?.username || !credentials?.password) {
          return null;
        }

        // Простий тест - в реальному додатку тут буде запит до API
        if (credentials.username === "testuser" && credentials.password === "testpass123") {
          return {
            id: "1",
            name: "Test User",
            email: "test@mfinance.com",
          };
        }

        if (credentials.username === "admin" && credentials.password === "admin123") {
          return {
            id: "2", 
            name: "Admin User",
            email: "admin@mfinance.com",
          };
        }

        return null;
      }
    }),
  ],
  session: { strategy: "jwt" },
  callbacks: {
    async jwt({ token, account, profile }) {
      if (account) {
        token.accessToken = account.access_token;
      }
      if (profile) {
        token.name = profile.name ?? token.name;
        token.email = profile.email ?? token.email;
      }
      return token;
    },
    async session({ session, token }) {
      session.accessToken = token.accessToken;
      return session;
    },
  },
  secret: process.env.NEXTAUTH_SECRET,
};

const handler = NextAuth(authOptions);

export { handler as GET, handler as POST };


