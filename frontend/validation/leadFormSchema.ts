import { z } from "zod";

export const leadFormSchema = z.object({
  name: z.string().min(1, "minimum of 1"),
  email: z.string().email("must be a valid email address"),
  phone: z.string().optional(),
  company: z.string().optional(),
  position: z.string().optional(),
  linkedin_profile: z.string().optional(),
  public_data: z.string().optional(), // Adjust this based on your requirements
});

export type LeadFormSchema = z.infer<typeof leadFormSchema>;
