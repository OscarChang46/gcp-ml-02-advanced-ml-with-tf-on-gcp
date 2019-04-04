
# coding: utf-8

# ## Content Based Filtering by hand
# 
# This lab illustrates how to implement a content based filter using low level Tensorflow operations.  
# The code here follows the technique explained in Module 2 of Recommendation Engines: Content Based Filtering.
# 
# 

# In[1]:


import numpy as np
import tensorflow as tf

tf.reset_default_graph()
print(tf.__version__)


# To start, we'll create our list of users, movies and features. While the users and movies represent elements in our database, for a content-based filtering method the features of the movies are likely hand-engineered and rely on domain knowledge to provide the best embedding space. Here we use the categories of Action, Sci-Fi, Comedy, Cartoon, and Drama to describe our movies (and thus our users).
# 
# In this example, we will assume our database consists of four users and six movies, listed below.  

# In[2]:


users = ['Ryan', 'Danielle',  'Vijay', 'Chris']
movies = ['Star Wars', 'The Dark Knight', 'Shrek', 'The Incredibles', 'Bleu', 'Memento']
features = ['Action', 'Sci-Fi', 'Comedy', 'Cartoon', 'Drama']

num_users = len(users)
num_movies = len(movies)
num_feats = len(features)


# ### Initialize our users, movie ratings and features
# 
# We'll need to enter the user's movie ratings and the k-hot encoded movie features matrix. Each row of the users_movies matrix represents a single user's rating (from 1 to 10) for each movie. A zero indicates that the user has not seen/rated that movie. The movies_feats matrix contains the features for each of the given movies. Each row represents one of the six movies, the columns represent the five categories. A one indicates that a movie fits within a given genre/category. 

# In[3]:


# each row represents a user's rating for the different movies
# e.g. rows represent users ['Ryan', 'Danielle',  'Vijay', 'Chris']
#      columns represent movies ['Star Wars', 'The Dark Knight', 'Shrek', 'The Incredibles', 'Bleu', 'Memento']
users_movies = [[4,  6,  8,  0, 0, 0],
                [0,  0, 10,  0, 8, 3],
                [0,  6,  0,  0, 3, 7],
                [10, 9,  0,  5, 0, 2]]

# features of the movies one-hot encoded
# e.g. columns represent ['Action', 'Sci-Fi', 'Comedy', 'Cartoon', 'Drama']
movies_feats = [[1, 1, 0, 0, 1],
                [1, 1, 0, 0, 0],
                [0, 0, 1, 1, 0],
                [1, 0, 1, 1, 0],
                [0, 0, 0, 0, 1],
                [1, 0, 0, 0, 1]]


# ### Computing the user feature matrix
# 
# One goal of this lab is to familiarize ourselves with low-level tensorflow operations, so we create tensorflow constants to represent the user-movie interaction and movie-feature matrices above.  
# Through the subsequent cells, we will compute the user feature matrix; that is, a matrix containing each user's embedding in the five-dimensional feature space. 
# Complete the TODOs to compute the requested tensors as illustrated in the Content Based Filtering module slides. 

# In[4]:


users_movies = tf.constant(users_movies, dtype = tf.float32)
movies_feats = tf.constant(movies_feats, dtype = tf.float32)


# In[10]:


#TODO (done): Create a list of weighted feature matrices for each user. 
# For each row of the user-movie interaction matrix, scale the corresponding row 
# of the movie-feature matrix to get the weighted feature matrix for each user.
wgtd_feature_matrices = [
  tf.expand_dims(
    tf.transpose(users_movies)[:, i], axis = 1) * movies_feats
  for i in range(num_users)
]

#TODO (done): Stack the collection of wgtd_feature_matrices you computed above to obtain the 
# full users movie feature tensor.
users_movies_feats = tf.stack(wgtd_feature_matrices, axis = 0)
                     


# To determine where each user lies in the feature embedding space, we compute the user-feature vectors by normalizing each user-feature vector. Complete the TODO in the following cell to find the full user-feature tensor; that is, a tensor where each row represents a single user's feature embedding. 

# In[13]:


users_movies_feats_sums = tf.reduce_sum(users_movies_feats, axis = 1)
users_movies_feats_totals = tf.reduce_sum(users_movies_feats_sums, axis = 1)

#TODO: Normalize the users_movies_feats tensor above for each user and aggregate 
# to get the 'user profile' across the five features.
# Hint: Divide these two quantities to normalize each feature. Use tf.stack to 
# combine each user-feature vector into a single rank-2 tensor. 
users_feats = tf.stack(
  [
    users_movies_feats_sums[i, :] / users_movies_feats_totals[i]
    for i in range(num_users)
  ], axis = 0
)


# #### Ranking feature relevance for each user
# 
# We can use the users_feats computed above to represent the relative importance of each movie category for each user. To do this, we'll make a small helper function below that finds the rank ordered movie features for a given user. 

# In[14]:


def find_user_top_feats(user_index):
    # returns a list of the rank ordered features of most importance for a given user
    feats_ind = tf.nn.top_k(users_feats[user_index], num_feats)[1]
    return tf.gather_nd(features, tf.expand_dims(feats_ind, axis = 1))


# We'll create a tensorflow session to compute these values.

# In[15]:


with tf.Session() as sess:
  sess.run(tf.global_variables_initializer())
  users_topfeats = {}
  for i in range(num_users):
    top_feats = sess.run(find_user_top_feats(i))
    users_topfeats[users[i]] = list(top_feats)


# The dictionary users_topfeats provides the most important movie features for each user. For example, we can see for Chris, the category 'Action' has a strong influence on the movies he's rated highly. The category of Cartoons is less relevant.

# In[16]:


users_topfeats


# ### Determining movie recommendations. 
# 
# We'll now use the user-feature tensor we computed above to determine the movie ratings and recommendations for each user.
# 
# To compute the projected ratings for each movie, we compute the similarity measure between the user's feature vector and the corresponding movie feature vector.  
# We will use the dot product as our similarity measure. In essence, this is a weighted movie average for each user. Complete the TODOs in the following cell.

# In[17]:


users_feats


# In[19]:


#TODO: Compute the dot product similarity between each row of the 
# users_feats matrix and each row of the movies_feats matrix.
# Hint: the tf.map_fn applies a given lambda function to a list of tensors. 
# The operation tf.tensordot computes the dot product between two tensors. Use the tf.tensordot 
# operation and specify the axes=1, since each row of these matrices is a rank-1 tensor.
users_ratings = [
  tf.map_fn(lambda x: tf.tensordot(users_feats[i, :], x, axes = 1),
            tf.cast(movies_feats, tf.float32))
  for i in range(num_users)
]

all_users_ratings = tf.stack(users_ratings)


# The computation above finds the similarity measure between each user and each movie in our database. To focus only on the ratings for new movies, we apply a mask to the all_users_ratings matrix.  
# If a user has already rated a movie, we ignore that rating. This way, we only focus on ratings for previously unseen/unrated movies.

# In[20]:


all_users_ratings_new = tf.where(tf.equal(users_movies, tf.zeros_like(users_movies)),
                                  all_users_ratings,
                                  -np.inf*tf.ones_like(tf.cast(users_movies, tf.float32)))


# The helper function below uses the users ratings matrix we computed above, to determine the index of the top movie recommendations for each user.

# In[21]:


def find_user_top_movies(user_index, num_to_recommend):
    # returns the top movie recommendations for given user index
    movies_ind = tf.nn.top_k(all_users_ratings_new[user_index], num_to_recommend)[1]
    return tf.gather_nd(movies, tf.expand_dims(movies_ind, axis = 1))


# As before, we create a tf.Session to compute the movie recommendations. 

# In[22]:


with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    user_topmovies = {}
    num_to_recommend = tf.reduce_sum(tf.cast(tf.equal(users_movies, 
                                                      tf.zeros_like(users_movies)), dtype = tf.float32), axis = 1)
    for ind in range(num_users):
      top_movies = sess.run(find_user_top_movies(ind, tf.cast(num_to_recommend[ind], dtype = tf.int32)))
      user_topmovies[users[ind]] = list(top_movies)         


# In[23]:


user_topmovies


# The user_topmovies dictionary now holds the recommendations we should make for each user. For example, for Danielle, we would recommend the movie The Incredibles as a top pick, followed by Star Wars and then The Dark Knight.