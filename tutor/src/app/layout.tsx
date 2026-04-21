import type { Metadata } from "next";
import { CopilotKit } from "@copilotkit/react-core";
import "./globals.css";

export const metadata: Metadata = {
  title: "Amazon Bedrock Workshop",
  description: "Interactive AI Tutor powered by Amazon Bedrock",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <CopilotKit runtimeUrl="/api/copilotkit" agent="strands_agent">
          {children}
        </CopilotKit>
      </body>
    </html>
  );
}
