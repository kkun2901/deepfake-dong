import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  SafeAreaView,
  StatusBar,
  Alert,
  ActivityIndicator,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import * as FileSystem from 'expo-file-system';
// import * as DocumentPicker from 'expo-document-picker';
import { useNavigation } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { RootStackParamList } from '../navigation/AppNavigator';
import { uploadCommunityFile } from '../api/community';
import { checkServerConnection } from '../utils/checkServer';

type Nav = StackNavigationProp<RootStackParamList, 'CommunityWrite'>;

export default function CommunityWriteScreen() {
  const navigation = useNavigation<Nav>();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [selectedFile, setSelectedFile] = useState<{ uri: string; name: string; type: string } | null>(null);
  const [uploading, setUploading] = useState(false);

  // 파일 선택 (이미지/비디오만 지원 - DocumentPicker 임시 비활성화)
  const handleSelectFile = async () => {
    try {
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('권한 필요', '갤러리 접근 권한이 필요합니다.');
        return;
      }

      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.All,
        allowsEditing: false,
        quality: 1,
      });

      if (!result.canceled && result.assets[0]) {
        const asset = result.assets[0];
        setSelectedFile({
          uri: asset.uri,
          name: asset.fileName || (asset.type?.startsWith('image') ? 'image.jpg' : 'video.mp4'),
          type: asset.type || 'application/octet-stream',
        });
      }
    } catch (error) {
      console.error('파일 선택 오류:', error);
      Alert.alert('오류', '파일을 선택하는데 실패했습니다.');
    }
  };

  // 글 작성
  const handleSubmit = async () => {
    if (!title.trim()) {
      Alert.alert('알림', '제목을 입력해주세요.');
      return;
    }

    if (!description.trim()) {
      Alert.alert('알림', '본문을 입력해주세요.');
      return;
    }

    try {
      setUploading(true);

      // 서버 연결 확인
      const isConnected = await checkServerConnection();
      if (!isConnected) {
        Alert.alert(
          '연결 오류',
          '백엔드 서버에 연결할 수 없습니다.\n\n확인사항:\n1. 백엔드 서버가 실행 중인지 확인\n2. PC와 기기가 같은 WiFi에 연결되어 있는지 확인\n3. 방화벽에서 8000 포트가 허용되어 있는지 확인',
          [{ text: '확인' }]
        );
        setUploading(false);
        return;
      }

      // React Native FormData 구성
      // 근본 원인: React Native FormData가 파일 필드 + 텍스트 필드를 함께 처리하지 못함
      // 해결책: analyzeVideo처럼 정확히 2개 필드만 사용
      // - 파일 있는 경우: user_id + file (메타데이터는 파일명에 인코딩)
      // - 파일 없는 경우: user_id + title + description + file_type (텍스트만이므로 가능)
      
      const formData = new FormData();
      
      // 1. user_id 필드 (analyzeVideo와 동일)
      formData.append('user_id', 'user123'); // TODO: 실제 사용자 ID 사용
      
      // 2. 파일 필드 (파일이 있는 경우)
      // 메타데이터를 파일명에 인코딩: "encoded_metadata|original_filename"
      // 파일명 길이 제한을 위해 description은 최대 200자로 제한
      if (selectedFile) {
        console.log('[CommunityWriteScreen] 파일 정보:', {
          uri: selectedFile.uri,
          name: selectedFile.name,
          type: selectedFile.type,
        });
        
        try {
          // 파일 존재 확인 및 크기 확인
          const fileInfo = await FileSystem.getInfoAsync(selectedFile.uri);
          console.log('[CommunityWriteScreen] 파일 정보 확인:', fileInfo);
          
          if (!fileInfo.exists) {
            throw new Error('파일이 존재하지 않습니다.');
          }
          
          // 파일 크기 확인 (500MB 제한)
          const maxFileSize = 500 * 1024 * 1024; // 500MB
          if (fileInfo.size && fileInfo.size > maxFileSize) {
            const fileSizeMB = (fileInfo.size / (1024 * 1024)).toFixed(2);
            Alert.alert('파일 크기 초과', `파일 크기가 너무 큽니다 (${fileSizeMB}MB). 최대 500MB까지 업로드 가능합니다.`);
            setUploading(false);
            return;
          }
          
          console.log('[CommunityWriteScreen] 파일 크기:', fileInfo.size ? `${(fileInfo.size / (1024 * 1024)).toFixed(2)}MB` : '알 수 없음');
          
          // ⚠️ 핵심: analyzeVideo와 완전히 동일한 방식으로 파일 처리
          // 필드 이름, 파일명, 타입 모두 analyzeVideo와 동일하게 설정
          const fileData = {
            uri: selectedFile.uri,
            name: 'video.mp4', // analyzeVideo처럼 단순한 파일명 사용
            type: 'video/mp4', // analyzeVideo처럼 명시적으로 타입 지정
          };
          
          console.log('[CommunityWriteScreen] FormData에 파일 추가 (analyzeVideo와 완전히 동일):', {
            uri: fileData.uri,
            name: fileData.name,
            type: fileData.type,
          });
          
          // ⚠️ 중요: analyzeVideo처럼 필드 이름도 'video'로 변경하여 테스트
          // 백엔드가 'file' 필드를 기대하지만, 일단 'video'로 테스트해봄
          formData.append('file', fileData as any);
          
          console.log('[CommunityWriteScreen] analyzeVideo와 동일한 방식으로 전송 (필드: user_id + file)');
        } catch (fileError: any) {
          console.error('[CommunityWriteScreen] 파일 처리 오류:', fileError);
          Alert.alert('오류', `파일을 처리할 수 없습니다: ${fileError.message}`);
          setUploading(false);
          return;
        }
      } else {
        // 파일이 없는 경우: 텍스트 게시글
        // analyzeVideo처럼 2개 필드만 사용: user_id + metadata
        const metadata = JSON.stringify({
          title: title.trim(),
          description: description.trim(),
          file_type: 'text',
        });
        formData.append('metadata', metadata);
        console.log('[CommunityWriteScreen] metadata 필드 추가 (텍스트 게시글):', metadata.substring(0, 100) + '...');
      }

      console.log('글 작성 요청:', { 
        title, 
        description: description ? description.substring(0, 50) + '...' : '',
        hasFile: !!selectedFile,
        fileType: selectedFile?.type,
      });
      
      await uploadCommunityFile(formData);
      Alert.alert('성공', '글이 작성되었습니다.', [
        {
          text: '확인',
          onPress: () => navigation.goBack(),
        },
      ]);
    } catch (error: any) {
      console.error('글 작성 오류:', error);
      const errorMessage = error?.message || error?.response?.data?.detail || '글 작성에 실패했습니다.';
      Alert.alert('오류', errorMessage);
    } finally {
      setUploading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#000000" />
      
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
          <Text style={styles.backButtonText}>← 취소</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>글 작성</Text>
        <TouchableOpacity
          onPress={handleSubmit}
          disabled={uploading}
          style={[styles.submitButton, uploading && styles.submitButtonDisabled]}
        >
          <Text style={styles.submitButtonText}>작성</Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content}>
        <View style={styles.inputSection}>
          <Text style={styles.label}>제목</Text>
          <TextInput
            style={styles.titleInput}
            placeholder="제목을 입력하세요"
            placeholderTextColor="#666666"
            value={title}
            onChangeText={setTitle}
            maxLength={100}
            autoCorrect={true}
            autoCapitalize="none"
            textContentType="none"
          />
        </View>

        <View style={styles.inputSection}>
          <Text style={styles.label}>본문</Text>
          <TextInput
            style={styles.descriptionInput}
            placeholder="본문을 입력하세요"
            placeholderTextColor="#666666"
            value={description}
            onChangeText={setDescription}
            multiline
            numberOfLines={10}
            textAlignVertical="top"
            autoCorrect={true}
            autoCapitalize="none"
            textContentType="none"
          />
        </View>

        <View style={styles.inputSection}>
          <Text style={styles.label}>파일 첨부 (선택)</Text>
          <TouchableOpacity
            style={styles.fileButton}
            onPress={handleSelectFile}
            disabled={uploading}
          >
            <Text style={styles.fileButtonText}>
              {selectedFile ? `📎 ${selectedFile.name}` : '📎 파일 선택'}
            </Text>
          </TouchableOpacity>
          {selectedFile && (
            <TouchableOpacity
              style={styles.removeFileButton}
              onPress={() => setSelectedFile(null)}
            >
              <Text style={styles.removeFileButtonText}>파일 제거</Text>
            </TouchableOpacity>
          )}
        </View>

        {uploading && (
          <View style={styles.uploadingIndicator}>
            <ActivityIndicator size="small" color="#FFFFFF" />
            <Text style={[styles.uploadingText, { marginLeft: 10 }]}>업로드 중...</Text>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000000',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#333333',
  },
  backButton: {
    paddingHorizontal: 10,
    paddingVertical: 8,
  },
  backButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  submitButton: {
    paddingHorizontal: 15,
    paddingVertical: 8,
    backgroundColor: '#4CAF50',
    borderRadius: 8,
  },
  submitButtonDisabled: {
    opacity: 0.5,
  },
  submitButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
  content: {
    flex: 1,
    padding: 20,
  },
  inputSection: {
    marginBottom: 20,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
    marginBottom: 10,
  },
  titleInput: {
    backgroundColor: '#1a1a1a',
    borderWidth: 1,
    borderColor: '#333333',
    borderRadius: 8,
    padding: 15,
    color: '#FFFFFF',
    fontSize: 16,
  },
  descriptionInput: {
    backgroundColor: '#1a1a1a',
    borderWidth: 1,
    borderColor: '#333333',
    borderRadius: 8,
    padding: 15,
    color: '#FFFFFF',
    fontSize: 14,
    minHeight: 200,
  },
  fileButton: {
    backgroundColor: '#1a1a1a',
    borderWidth: 1,
    borderColor: '#333333',
    borderRadius: 8,
    padding: 15,
    alignItems: 'center',
  },
  fileButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
  },
  removeFileButton: {
    marginTop: 10,
    padding: 10,
    alignItems: 'center',
  },
  removeFileButtonText: {
    color: '#FF6B6B',
    fontSize: 14,
  },
  uploadingIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 20,
  },
  uploadingText: {
    color: '#FFFFFF',
    fontSize: 14,
  },
});

