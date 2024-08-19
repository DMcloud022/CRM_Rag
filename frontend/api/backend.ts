import crypto from 'crypto';

// Interfaces
interface PublicDataPayload {
  email: string;
  linkedin_profile: string;
}

interface CrmData {
  name: string;
  email: string;
  phone: string;
  company: string;
  position: string;
  linkedin_profile: string;
  public_data?: Record<string, unknown>;
}

// Utility functions
function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

function validateUrl(url: string): boolean {
  const urlRegex = /^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_+.~#?&//=]*)$/;
  return urlRegex.test(url);
}

function validateCrmData(data: CrmData): boolean {
  const requiredFields: (keyof CrmData)[] = ["name", "email", "phone", "company", "position", "linkedin_profile"];
  return requiredFields.every(field => field in data);
}

// Error handling
function handleFetchError(response: Response): void {
  if (!response.ok) {
    throw new Error(`API request failed: ${response.statusText}`);
  }
}

// API functions
export async function scanBusinessCard(imageBinary: Buffer): Promise<Record<string, unknown>> {
  const response = await fetch('http://localhost:8000/scan-business-card', {
    method: 'POST',
    body: imageBinary,
    headers: {
      // Add necessary headers here
      'Content-Type': 'application/octet-stream',
    },
  });
  handleFetchError(response);
  return response.json();
}

export async function gatherPublicData(payload: PublicDataPayload): Promise<Record<string, unknown>> {
  if (!validateEmail(payload.email)) {
    throw new Error("Invalid email address");
  }
  if (!validateUrl(payload.linkedin_profile)) {
    throw new Error("Invalid LinkedIn profile URL");
  }

  const response = await fetch('http://localhost:8000/gather-public-data', {
    method: 'POST',
    body: JSON.stringify(payload),
    headers: {
      'Content-Type': 'application/json',
      // Add other necessary headers here
    },
  });
  handleFetchError(response);
  return response.json();
}

export async function sendToCrm(crmName: string, data: CrmData): Promise<Record<string, unknown>> {
  if (!validateCrmData(data)) {
    throw new Error("Invalid CRM data");
  }

  const response = await fetch(`http://localhost:8000/send-to-crm/${crmName}`, {
    method: 'POST',
    body: JSON.stringify(data),
    headers: {
      'Content-Type': 'application/json',
      // Add other necessary headers here
    },
  });
  handleFetchError(response);
  return response.json();
}

export async function initiateOauth(crmName: string): Promise<string> {
  console.log(crmName);
  const response = await fetch(`http://localhost:8000/oauth/${crmName}/initiate`, {
    method: 'GET',
  });
  handleFetchError(response);
  return response.json(); 
}

export async function oauthCallback(crmName: string, code: string): Promise<Record<string, unknown>> {
  const response = await fetch(`http://localhost:8000/oauth/${crmName}/callback?code=${code}`, {
    method: 'GET',
  });
  handleFetchError(response);
  return response.json();
}

export async function createLead(crmName: string, leadData: CrmData): Promise<Record<string, unknown>> {
  if (!validateCrmData(leadData)) {
    throw new Error("Invalid lead data");
  }

  const response = await fetch(`http://localhost:8000/create-${crmName}-lead`, {
    method: 'POST',
    body: JSON.stringify(leadData),
    headers: {
      'Content-Type': 'application/json',
      // Add other necessary headers here
    },
  });
  handleFetchError(response);
  return response.json();
}

// Example usage
// async function main() {
//   try {
//     // Your main logic here
//   } catch (error) {
//     if (error instanceof Error) {
//       console.error(`Error: ${error.message}`);
//     } else {
//       console.error('An unexpected error occurred');
//     }
//   }
// }

// Uncomment the following line to run the example
// main();
