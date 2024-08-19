import React from "react";
import LeadForm from "@/components/forms/LeadForm";
import { SafeAreaView } from "react-native-safe-area-context";

const LeadFormScreen: React.FC = () => {
  const redirectTo = "/sign-in";

  return (
    <SafeAreaView className="flex-1">
      <LeadForm redirectTo={redirectTo} />
    </SafeAreaView>
  );
};

export default LeadFormScreen;
