import React, { useState } from 'react';
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
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { RootStackParamList } from '../navigation/AppNavigator';
import { getCommunityPosts, CommunityPost } from '../api/community';

type Nav = StackNavigationProp<RootStackParamList, 'Community'>;

export default function CommunityScreen() {
  const navigation = useNavigation<Nav>();
  const [posts, setPosts] = useState<CommunityPost[]>([]);
  const [loading, setLoading] = useState(false);

  // 커뮤니티 게시글 목록 불러오기
  const loadPosts = async () => {
    try {
      setLoading(true);
      const data = await getCommunityPosts();
      setPosts(data);
    } catch (error) {
      console.error('게시글 불러오기 실패:', error);
      Alert.alert('오류', '게시글을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 컴포넌트 마운트 시 게시글 불러오기
  React.useEffect(() => {
    loadPosts();
  }, []);

  // 포커스 시 게시글 새로고침
  React.useEffect(() => {
    const unsubscribe = navigation.addListener('focus', () => {
      loadPosts();
    });
    return unsubscribe;
  }, [navigation]);

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#000000" />
      
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.navigate('Home')} style={styles.backButton}>
          <Text style={styles.backButtonText}>← 홈</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>커뮤니티</Text>
        <TouchableOpacity onPress={() => navigation.navigate('CommunityWrite')} style={styles.writeButton}>
          <Text style={styles.writeButtonText}>글 작성</Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content}>
        {loading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#FFFFFF" />
          </View>
        ) : posts.length === 0 ? (
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>아직 게시글이 없습니다.</Text>
            <Text style={styles.emptySubText}>첫 번째 글을 작성해보세요!</Text>
          </View>
        ) : (
          posts.map((post) => (
            <TouchableOpacity
              key={post.id}
              style={styles.postItem}
              onPress={() => navigation.navigate('CommunityDetail', { postId: post.id })}
            >
              <Text style={styles.postTitle}>{post.title}</Text>
              <View style={styles.postMeta}>
                <Text style={styles.postAuthor}>{post.user_id}</Text>
                <Text style={styles.postDate}>
                  {new Date(post.created_at).toLocaleDateString('ko-KR')}
                </Text>
              </View>
            </TouchableOpacity>
          ))
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
  writeButton: {
    paddingHorizontal: 15,
    paddingVertical: 8,
    backgroundColor: '#4CAF50',
    borderRadius: 8,
  },
  writeButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
  content: {
    flex: 1,
  },
  loadingContainer: {
    padding: 40,
    alignItems: 'center',
  },
  emptyContainer: {
    padding: 40,
    alignItems: 'center',
  },
  emptyText: {
    color: '#FFFFFF',
    fontSize: 16,
    marginBottom: 8,
  },
  emptySubText: {
    color: '#888888',
    fontSize: 14,
  },
  postItem: {
    paddingHorizontal: 20,
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#1a1a1a',
    backgroundColor: '#0a0a0a',
  },
  postTitle: {
    fontSize: 16,
    color: '#FFFFFF',
    marginBottom: 8,
  },
  postMeta: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  postAuthor: {
    fontSize: 12,
    color: '#888888',
  },
  postDate: {
    fontSize: 12,
    color: '#888888',
  },
});
