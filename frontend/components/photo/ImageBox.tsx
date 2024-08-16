import React from "react";
import { View, Text, Image } from "react-native";

interface ImageBoxProps {
  uri?: string;
}

const ImageBox: React.FC<ImageBoxProps> = ({ uri }) => {
  return (
    <View className="w-72 h-72 bg-gray-200 border border-gray-300 rounded flex items-center justify-center">
      {uri ? (
        <Image source={{ uri }} className="w-full h-full rounded" />
      ) : (
        <Text className="text-black-500">No Photo</Text>
      )}
    </View>
  );
};

export default ImageBox;
