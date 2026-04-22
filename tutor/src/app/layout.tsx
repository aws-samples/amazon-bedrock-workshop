import type { Metadata } from "next";
import { CopilotKit } from "@copilotkit/react-core";
import "./globals.css";

export const metadata: Metadata = {
  title: "Amazon Bedrock Workshop",
  description: "Interactive AI Tutor powered by Amazon Bedrock",
};

// When running behind SageMaker Studio proxy, set NEXT_PUBLIC_COPILOTKIT_URL
// to the full proxied URL, e.g.:
// https://<domain>.studio.us-west-2.sagemaker.aws/jupyterlab/default/proxy/3000/api/copilotkit
const runtimeUrl = process.env.NEXT_PUBLIC_COPILOTKIT_URL || "/api/copilotkit";

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <CopilotKit runtimeUrl={runtimeUrl} agent="strands_agent">
          {children}
        </CopilotKit>
      </body>
    </html>
  );
}
