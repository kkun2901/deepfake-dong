import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
  StatusBar,
  Alert,
  ActivityIndicator,
  Linking,
} from 'react-native';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { RootStackParamList } from '../navigation/AppNavigator';
import { getCommunityPost, CommunityPost } from '../api/community';
import * as FileSystem from 'expo-file-system';

type Nav = StackNavigationProp<RootStackParamList, 'CommunityDetail'>;
type DetailRouteProp = RouteProp<RootStackParamList, 'CommunityDetail'>;

export default function CommunityDetailScreen() {
  const navigation = useNavigation<Nav>();
  const route = useRoute<DetailRouteProp>();
  const { postId } = route.params;

  const [post, setPost] = useState<CommunityPost | null>(null);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);

  // 게시글 불러오기
  const loadPost = async () => {
    try {
      setLoading(true);
      const data = await getCommunityPost(postId);
      setPost(data);
    } catch (error) {
      console.error('게시글 불러오기 실패:', error);
      Alert.alert('오류', '게시글을 불러오는데 실패했습니다.');
      navigation.goBack();
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPost();
  }, [postId]);

  // 파일 다운로드
  const handleDownloadFile = async () => {
    if (!post?.file_url) {
      Alert.alert('알림', '다운로드할 파일이 없습니다.');
      return;
    }

    try {
      setDownloading(true);

      // 파일 다운로드
      const fileUri = FileSystem.documentDirectory + (post.file_name || 'downloaded_file');
      const downloadResult = await FileSystem.downloadAsync(post.file_url, fileUri);

      if (downloadResult.status === 200) {
        Alert.alert(
          '다운로드 완료',
          `파일이 다운로드되었습니다.\n경로: ${downloadResult.uri}`,
          [
            {
              text: '확인',
              onPress: () => {
                // Android에서 파일을 열기
                Linking.openURL(downloadResult.uri);
              },
            },
          ]
        );
      } else {
        throw new Error('다운로드 실패');
      }
    } catch (error) {
      console.error('파일 다운로드 오류:', error);
      Alert.alert('오류', '파일 다운로드에 실패했습니다.');
    } finally {
      setDownloading(false);
    }
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <StatusBar barStyle="light-content" backgroundColor="#000000" />
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#FFFFFF" />
        </View>
      </SafeAreaView>
    );
  }

  if (!post) {
    return (
      <SafeAreaView style={styles.container}>
        <StatusBar barStyle="light-content" backgroundColor="#000000" />
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>게시글을 찾을 수 없습니다.</Text>
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => navigation.goBack()}
          >
            <Text style={styles.backButtonText}>돌아가기</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#000000" />
      
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.navigate('Community')} style={styles.backButton}>
          <Text style={styles.backButtonText}>← 커뮤니티</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>게시글</Text>
        <View style={styles.headerRight} />
      </View>

      <ScrollView style={styles.content}>
        <View style={styles.postContainer}>
          <Text style={styles.postTitle}>{post.title}</Text>
          
          <View style={styles.postMeta}>
            <Text style={styles.postAuthor}>작성자: {post.user_id}</Text>
            <Text style={styles.postDate}>
              {new Date(post.created_at).toLocaleString('ko-KR')}
            </Text>
          </View>

          <View style={styles.divider} />

          <Text style={styles.postDescription}>{post.description}</Text>

          {post.file_url && (
            <>
              <View style={styles.divider} />
              <View style={styles.fileSection}>
                <Text style={styles.fileLabel}>첨부 파일</Text>
                <Text style={styles.fileName} numberOfLines={1}>
                  {post.file_name || '파일'}
                </Text>
                <TouchableOpacity
                  style={[styles.downloadButton, downloading && styles.downloadButtonDisabled]}
                  onPress={handleDownloadFile}
                  disabled={downloading}
                >
                  {downloading ? (
                    <ActivityIndicator size="small" color="#FFFFFF" />
                  ) : (
                    <Text style={styles.downloadButtonText}>📥 다운로드</Text>
                  )}
                </TouchableOpacity>
              </View>
            </>
          )}
        </View>
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
  headerRight: {
    width: 80,
  },
  content: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  errorText: {
    color: '#FFFFFF',
    fontSize: 16,
    marginBottom: 20,
  },
  postContainer: {
    padding: 20,
  },
  postTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 15,
  },
  postMeta: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 15,
  },
  postAuthor: {
    fontSize: 14,
    color: '#888888',
  },
  postDate: {
    fontSize: 14,
    color: '#888888',
  },
  divider: {
    height: 1,
    backgroundColor: '#333333',
    marginVertical: 20,
  },
  postDescription: {
    fontSize: 16,
    color: '#CCCCCC',
    lineHeight: 24,
  },
  fileSection: {
    marginTop: 10,
  },
  fileLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
    marginBottom: 10,
  },
  fileName: {
    fontSize: 14,
    color: '#CCCCCC',
    marginBottom: 15,
  },
  downloadButton: {
    backgroundColor: '#4CAF50',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 8,
    alignItems: 'center',
  },
  downloadButtonDisabled: {
    opacity: 0.5,
  },
  downloadButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
});

