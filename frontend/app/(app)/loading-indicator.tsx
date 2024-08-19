import { ActivityIndicator, Text } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

const UploadFile: React.FC = () => {
  return (
    <SafeAreaView className="flex-1 justify-center items-center bg-white">
      <ActivityIndicator size="large" color="#4A00E0" />
      <Text className="mt-2 font-semibold text-[#4A00E0]">
        extracting lead details...
      </Text>
    </SafeAreaView>
  );
};

export default UploadFile;
