import { ActivityIndicator, Text, View } from "react-native";

const UploadFile: React.FC = () => {
  return (
    <View className="flex-1 justify-center items-center bg-white">
      <ActivityIndicator size="large" color="#4A00E0" />
      <Text className="mt-2 font-semibold text-[#4A00E0]">transcribing...</Text>
    </View>
  );
};

export default UploadFile;
