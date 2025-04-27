# Minecraft MCP Server Database Schema

## Overview

This document details the database schema for the Minecraft MCP server using Supabase PostgreSQL. The schema is designed to support template management, world configuration, and operation tracking for procedural generation in Minecraft.

## Tables

### Users

The users table is managed by Supabase Auth and contains user authentication information.

```sql
-- This table is managed by Supabase Auth
CREATE TABLE auth.users (
  id UUID PRIMARY KEY,
  email TEXT UNIQUE,
  encrypted_password TEXT,
  email_confirmed_at TIMESTAMP WITH TIME ZONE,
  invited_at TIMESTAMP WITH TIME ZONE,
  confirmation_token TEXT,
  confirmation_sent_at TIMESTAMP WITH TIME ZONE,
  recovery_token TEXT,
  recovery_sent_at TIMESTAMP WITH TIME ZONE,
  email_change_token TEXT,
  email_change_sent_at TIMESTAMP WITH TIME ZONE,
  last_sign_in_at TIMESTAMP WITH TIME ZONE,
  raw_app_meta_data JSONB,
  raw_user_meta_data JSONB,
  is_super_admin BOOLEAN,
  created_at TIMESTAMP WITH TIME ZONE,
  updated_at TIMESTAMP WITH TIME ZONE,
  phone TEXT UNIQUE,
  phone_confirmed_at TIMESTAMP WITH TIME ZONE,
  phone_change TEXT,
  phone_change_token TEXT,
  phone_change_sent_at TIMESTAMP WITH TIME ZONE,
  confirmed_at TIMESTAMP WITH TIME ZONE,
  email_change TEXT
);
```

### User Profiles

Extends the Supabase Auth users table with additional user information.

```sql
CREATE TABLE user_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id),
  username TEXT UNIQUE NOT NULL,
  display_name TEXT,
  bio TEXT,
  avatar_url TEXT,
  minecraft_username TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Trigger to create profile on user creation
CREATE FUNCTION create_profile_for_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO user_profiles (id, username)
  VALUES (NEW.id, NEW.raw_user_meta_data->>'username');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE create_profile_for_user();
```

### Templates

Stores structure templates created by users.

```sql
CREATE TABLE templates (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  tags TEXT[],
  blueprint JSONB NOT NULL,
  dimensions INTEGER[3],
  preview_url TEXT,
  public BOOLEAN DEFAULT false,
  featured BOOLEAN DEFAULT false,
  downloads INTEGER DEFAULT 0,
  likes INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  CONSTRAINT template_name_user_id_key UNIQUE (name, user_id)
);

-- Index for searching templates
CREATE INDEX templates_tags_idx ON templates USING GIN (tags);
CREATE INDEX templates_name_description_idx ON templates USING GIN (to_tsvector('english', name || ' ' || COALESCE(description, '')));
```

### Template Components

Reusable building components that can be included in templates.

```sql
CREATE TABLE template_components (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  tags TEXT[],
  blueprint JSONB NOT NULL,
  dimensions INTEGER[3],
  preview_url TEXT,
  public BOOLEAN DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  CONSTRAINT component_name_user_id_key UNIQUE (name, user_id)
);

-- Index for searching components
CREATE INDEX template_components_tags_idx ON template_components USING GIN (tags);
```

### Template Likes

Tracks which users have liked which templates.

```sql
CREATE TABLE template_likes (
  template_id UUID REFERENCES templates(id) ON DELETE CASCADE,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  PRIMARY KEY (template_id, user_id)
);

-- Trigger to update likes count on templates
CREATE FUNCTION update_template_likes_count()
RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    UPDATE templates SET likes = likes + 1 WHERE id = NEW.template_id;
  ELSIF TG_OP = 'DELETE' THEN
    UPDATE templates SET likes = likes - 1 WHERE id = OLD.template_id;
  END IF;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_template_like_change
  AFTER INSERT OR DELETE ON template_likes
  FOR EACH ROW EXECUTE PROCEDURE update_template_likes_count();
```

### Worlds

Stores information about Minecraft worlds.

```sql
CREATE TABLE worlds (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  description TEXT,
  seed TEXT,
  settings JSONB,
  server_id TEXT,
  build_area JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### World Access

Controls which users have access to which worlds.

```sql
CREATE TABLE world_access (
  world_id UUID REFERENCES worlds(id) ON DELETE CASCADE,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  permission_level TEXT NOT NULL CHECK (permission_level IN ('read', 'write', 'admin')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  PRIMARY KEY (world_id, user_id)
);
```

### Generation History

Tracks terrain and structure generation operations.

```sql
CREATE TABLE generation_history (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  world_id UUID REFERENCES worlds(id) NOT NULL,
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  operation_type TEXT NOT NULL CHECK (operation_type IN ('terrain', 'structure', 'blocks')),
  region_x INTEGER,
  region_z INTEGER,
  parameters JSONB,
  blocks_modified INTEGER,
  status TEXT NOT NULL CHECK (status IN ('pending', 'in_progress', 'completed', 'failed')),
  error_message TEXT,
  started_at TIMESTAMP WITH TIME ZONE,
  completed_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for querying operations by world
CREATE INDEX generation_history_world_id_idx ON generation_history(world_id);
```

### Operations

Tracks long-running operations.

```sql
CREATE TABLE operations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  operation_type TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('pending', 'in_progress', 'completed', 'failed')),
  progress INTEGER DEFAULT 0,
  result JSONB,
  error_message TEXT,
  estimated_completion TIMESTAMP WITH TIME ZONE,
  started_at TIMESTAMP WITH TIME ZONE,
  completed_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Biomes

Stores biome definitions for world generation.

```sql
CREATE TABLE biomes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT UNIQUE NOT NULL,
  description TEXT,
  minecraft_id TEXT NOT NULL,
  temperature FLOAT,
  humidity FLOAT,
  terrain_params JSONB,
  vegetation_params JSONB,
  structure_params JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Generation Algorithms

Stores terrain generation algorithm definitions.

```sql
CREATE TABLE generation_algorithms (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT UNIQUE NOT NULL,
  description TEXT,
  version TEXT NOT NULL,
  parameters_schema JSONB NOT NULL,
  default_parameters JSONB NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Row-Level Security Policies

### Templates

```sql
-- Enable RLS on templates
ALTER TABLE templates ENABLE ROW LEVEL SECURITY;

-- Policy for viewing templates
CREATE POLICY template_select_policy ON templates
  FOR SELECT
  USING (
    public = true OR
    user_id = auth.uid() OR
    EXISTS (
      SELECT 1 FROM world_access
      WHERE user_id = auth.uid() AND permission_level IN ('write', 'admin')
    )
  );

-- Policy for inserting templates
CREATE POLICY template_insert_policy ON templates
  FOR INSERT
  WITH CHECK (user_id = auth.uid());

-- Policy for updating templates
CREATE POLICY template_update_policy ON templates
  FOR UPDATE
  USING (user_id = auth.uid());

-- Policy for deleting templates
CREATE POLICY template_delete_policy ON templates
  FOR DELETE
  USING (user_id = auth.uid());
```

### World Access

```sql
-- Enable RLS on world_access
ALTER TABLE world_access ENABLE ROW LEVEL SECURITY;

-- Policy for viewing world access
CREATE POLICY world_access_select_policy ON world_access
  FOR SELECT
  USING (
    user_id = auth.uid() OR
    EXISTS (
      SELECT 1 FROM world_access
      WHERE world_id = world_access.world_id AND user_id = auth.uid() AND permission_level = 'admin'
    )
  );

-- Policy for managing world access (admin only)
CREATE POLICY world_access_insert_policy ON world_access
  FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM world_access
      WHERE world_id = NEW.world_id AND user_id = auth.uid() AND permission_level = 'admin'
    )
  );

CREATE POLICY world_access_update_policy ON world_access
  FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM world_access
      WHERE world_id = world_access.world_id AND user_id = auth.uid() AND permission_level = 'admin'
    )
  );

CREATE POLICY world_access_delete_policy ON world_access
  FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM world_access
      WHERE world_id = world_access.world_id AND user_id = auth.uid() AND permission_level = 'admin'
    )
  );
```

## Database Functions

### Get User Templates

```sql
CREATE OR REPLACE FUNCTION get_user_templates(
  user_id UUID,
  search_term TEXT DEFAULT NULL,
  tag_filter TEXT[] DEFAULT NULL,
  limit_val INTEGER DEFAULT 20,
  offset_val INTEGER DEFAULT 0
)
RETURNS TABLE (
  id UUID,
  name TEXT,
  description TEXT,
  tags TEXT[],
  dimensions INTEGER[],
  preview_url TEXT,
  public BOOLEAN,
  featured BOOLEAN,
  downloads INTEGER,
  likes INTEGER,
  created_at TIMESTAMP WITH TIME ZONE,
  updated_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    t.id,
    t.name,
    t.description,
    t.tags,
    t.dimensions,
    t.preview_url,
    t.public,
    t.featured,
    t.downloads,
    t.likes,
    t.created_at,
    t.updated_at
  FROM
    templates t
  WHERE
    t.user_id = get_user_templates.user_id
    AND (search_term IS NULL OR 
         to_tsvector('english', t.name || ' ' || COALESCE(t.description, '')) @@ to_tsquery('english', search_term))
    AND (tag_filter IS NULL OR t.tags && tag_filter)
  ORDER BY
    t.updated_at DESC
  LIMIT limit_val
  OFFSET offset_val;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

### Increment Template Downloads

```sql
CREATE OR REPLACE FUNCTION increment_template_downloads(template_id UUID)
RETURNS VOID AS $$
BEGIN
  UPDATE templates
  SET downloads = downloads + 1
  WHERE id = template_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

## Database Views

### Public Templates

```sql
CREATE VIEW public_templates AS
SELECT
  t.id,
  t.name,
  t.description,
  t.tags,
  t.dimensions,
  t.preview_url,
  t.featured,
  t.downloads,
  t.likes,
  t.created_at,
  t.updated_at,
  p.username as creator_username,
  p.display_name as creator_display_name
FROM
  templates t
JOIN
  user_profiles p ON t.user_id = p.id
WHERE
  t.public = true;
```

### User World Access

```sql
CREATE VIEW user_world_access AS
SELECT
  w.id,
  w.name,
  w.description,
  w.seed,
  w.settings,
  w.server_id,
  w.build_area,
  w.created_at,
  w.updated_at,
  wa.permission_level
FROM
  worlds w
JOIN
  world_access wa ON w.id = wa.world_id
WHERE
  wa.user_id = auth.uid();
```

## Entity Relationship Diagram

```
+---------------+       +------------------+       +---------------+
| auth.users    |       | user_profiles    |       | templates     |
+---------------+       +------------------+       +---------------+
| id            |<----->| id               |       | id            |
| email         |       | username         |       | user_id       |<----+
| ...           |       | display_name     |       | name          |     |
+---------------+       | ...              |       | ...           |     |
                        +------------------+       +---------------+     |
                                                          ^              |
                                                          |              |
                        +------------------+              |              |
                        | template_likes   |              |              |
                        +------------------+              |              |
                        | template_id      |<-------------+              |
                        | user_id          |<----------------------------+
                        | ...              |                             |
                        +------------------+                             |
                                                                         |
+---------------+       +------------------+       +------------------+  |
| worlds        |       | world_access     |       | generation_history  |
+---------------+       +------------------+       +------------------+  |
| id            |<----->| world_id         |       | id               |  |
| name          |       | user_id          |<------| world_id         |  |
| ...           |       | permission_level |       | user_id          |<-+
+---------------+       +------------------+       | ...              |
                                                   +------------------+
```

## Indexes

```sql
-- Templates
CREATE INDEX templates_user_id_idx ON templates(user_id);
CREATE INDEX templates_public_idx ON templates(public) WHERE public = true;
CREATE INDEX templates_featured_idx ON templates(featured) WHERE featured = true;

-- Template Components
CREATE INDEX template_components_user_id_idx ON template_components(user_id);
CREATE INDEX template_components_public_idx ON template_components(public) WHERE public = true;

-- Generation History
CREATE INDEX generation_history_user_id_idx ON generation_history(user_id);
CREATE INDEX generation_history_status_idx ON generation_history(status);

-- Operations
CREATE INDEX operations_user_id_idx ON operations(user_id);
CREATE INDEX operations_status_idx ON operations(status);
CREATE INDEX operations_type_idx ON operations(operation_type);
```

## Migrations

Database migrations will be managed using Supabase migrations. Each migration will be versioned and applied in sequence to ensure consistent database schema across all environments.

Example migration file structure:

```
migrations/
├── 20250427000000_initial_schema.sql
├── 20250427000001_add_template_components.sql
├── 20250427000002_add_biomes_table.sql
└── 20250427000003_add_generation_algorithms.sql
```

## Backup and Recovery

Supabase provides automated daily backups with point-in-time recovery. Additional backup procedures will be implemented for critical data:

1. Weekly full database dumps stored in secure cloud storage
2. Template blueprints backed up separately as JSON files
3. Critical configuration data exported regularly

## Performance Considerations

1. **Indexing Strategy**: Indexes are created for frequently queried columns
2. **JSONB Optimization**: JSONB columns use GIN indexes for efficient querying
3. **Partitioning**: For large tables like `generation_history`, consider partitioning by date
4. **Connection Pooling**: Utilize Supabase's connection pooling for efficient resource usage
5. **Query Optimization**: Monitor and optimize slow queries using Supabase's query insights

## Security Considerations

1. **Row-Level Security**: All tables have RLS policies to restrict access
2. **Parameterized Queries**: All database access uses parameterized queries to prevent SQL injection
3. **Minimal Permissions**: Database functions use the principle of least privilege
4. **Encryption**: Sensitive data is encrypted at rest
5. **Audit Logging**: Critical operations are logged for security auditing