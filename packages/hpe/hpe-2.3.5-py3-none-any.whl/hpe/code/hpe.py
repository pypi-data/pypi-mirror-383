#!/usr/bin/env python3
"""
FreeFly GLB Viewer v9 - Importable Package Version

This module provides a 3D GLB/GLTF model viewer with object manipulation capabilities.
Can be used as a standalone application or imported as a package in other projects.

Classes:
    CubeOpenGLFrame: OpenGL rendering frame with 3D model display and manipulation
    FreeFlyApp: Main application class with UI and controls

Functions:
    create_viewer(): Factory function to create a new viewer instance
    run_standalone(): Run the application in standalone mode
"""

import customtkinter as ctk
from customtkinter import filedialog
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo
from pyopengltk import OpenGLFrame
import numpy as np
import trimesh
from PIL import Image
import traceback # For detailed error logging
import math # For camera calculations
import copy # For duplicating objects
import toml # For save/load functionality
import os # For file operations
import numba
from numba import jit
import time
import ctypes
import threading
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys

import pygame
pygame.init()
if pygame.display.get_init():
    pygame.display.quit()

# --- Terrain Editing Helper Functions ---
def screen_to_world_ray_glu(mouse_x, mouse_y, screen_width, screen_height, view_matrix, projection_matrix):
    """Convert screen coordinates to world ray for terrain interaction."""
    if screen_height == 0 or screen_width == 0:
        return np.array([0,0,0], dtype=np.float32), np.array([0,0,-1], dtype=np.float32)

    viewport = glGetIntegerv(GL_VIEWPORT)
    ogl_mouse_y = float(viewport[3] - mouse_y)

    view_matrix_double = np.array(view_matrix, dtype=np.float64)
    projection_matrix_double = np.array(projection_matrix, dtype=np.float64)

    try:
        near_tuple = gluUnProject(float(mouse_x), ogl_mouse_y, 0.0,
                                  model=view_matrix_double, proj=projection_matrix_double, view=viewport)
        far_tuple = gluUnProject(float(mouse_x), ogl_mouse_y, 1.0,
                                 model=view_matrix_double, proj=projection_matrix_double, view=viewport)
    except Exception as e:
        return np.array([0,0,0], dtype=np.float32), np.array([0,0,-1], dtype=np.float32)

    if near_tuple is None or far_tuple is None:
        return np.array([0,0,0], dtype=np.float32), np.array([0,0,-1], dtype=np.float32)

    origin = np.array(near_tuple, dtype=np.float32)
    far_point = np.array(far_tuple, dtype=np.float32)
    direction = far_point - origin
    norm = np.linalg.norm(direction)
    return origin, direction / norm if norm > 1e-8 else np.array([0,0,-1], dtype=np.float32)

def ray_terrain_intersection(ray_origin, ray_direction, terrain_obj, max_dist=4000.0):
    """Find intersection point between ray and terrain mesh."""
    if not terrain_obj or 'vertices' not in terrain_obj:
        return None

    vertices = terrain_obj['vertices']
    if len(vertices) == 0:
        return None

    # Get terrain bounds
    min_x, max_x = np.min(vertices[:, 0]), np.max(vertices[:, 0])
    min_z, max_z = np.min(vertices[:, 2]), np.max(vertices[:, 2])

    # Simple ray-mesh intersection using terrain bounds
    num_steps = 200
    step_size = max_dist / num_steps

    for i in range(1, num_steps + 1):
        current_t = i * step_size
        current_pos_on_ray = ray_origin + ray_direction * current_t

        # Check if ray point is within terrain bounds
        if (min_x <= current_pos_on_ray[0] <= max_x and
            min_z <= current_pos_on_ray[2] <= max_z):

            # Get terrain height at this position
            terrain_height = get_terrain_height_at_position(terrain_obj, current_pos_on_ray[0], current_pos_on_ray[2])
            if terrain_height is not None and current_pos_on_ray[1] <= terrain_height + 0.1:
                return np.array([current_pos_on_ray[0], terrain_height, current_pos_on_ray[2]], dtype=np.float32)

    return None

# --- Brush Shaders ---
BRUSH_VERTEX_SHADER = """
#version 330 core
layout (location = 0) in vec3 aPos;
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
void main()
{
    gl_Position = projection * view * model * vec4(aPos, 1.0);
}
"""

BRUSH_FRAGMENT_SHADER = """
#version 330 core
out vec4 FragColor;
uniform vec4 brushColor;
void main()
{
    FragColor = brushColor;
}
"""

# --- Brush Visualizer Class ---
class BrushVisualizer:
    def __init__(self, segments=32):
        self.segments = segments
        self.vertices = np.array([], dtype=np.float32)
        self.VAO, self.VBO = None, None
        self.shader_program = None
        self.model_matrix = np.identity(4, dtype=np.float32).T
        self.color = np.array([1.0, 1.0, 0.0, 0.7], dtype=np.float32)  # Yellow with transparency
        self.visible = True
        self.position = np.array([0, 0, 0], dtype=np.float32)
        self._generate_geometry()

    def _generate_geometry(self):
        vertices_list = []
        unit_radius = 1.0
        for i in range(self.segments):
            angle = i * (2 * math.pi / self.segments)
            x1, z1 = math.cos(angle) * unit_radius, math.sin(angle) * unit_radius
            angle_next = (i + 1) * (2 * math.pi / self.segments)
            x2, z2 = math.cos(angle_next) * unit_radius, math.sin(angle_next) * unit_radius
            vertices_list.extend([x1, 0.0, z1, x2, 0.0, z2])
        self.vertices = np.array(vertices_list, dtype=np.float32).reshape(-1, 3)

    def setup_buffers_gl(self):
        if self.VAO is not None:
            glDeleteVertexArrays(1, [self.VAO])
            if self.VBO is not None:
                glDeleteBuffers(1, [self.VBO])
        self.VAO = glGenVertexArrays(1)
        self.VBO = glGenBuffers(1)
        glBindVertexArray(self.VAO)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def set_shader(self, shader_program):
        self.shader_program = shader_program

    def update_transform(self, world_position, current_brush_radius):
        self.position = np.array(world_position, dtype=np.float32)

        rm_trans = np.array([
            [1, 0, 0, self.position[0]],
            [0, 1, 0, self.position[1]],
            [0, 0, 1, self.position[2]],
            [0, 0, 0, 1]
        ], dtype=np.float32)

        rm_scale = np.array([
            [current_brush_radius, 0, 0, 0],
            [0, 1, 0, 0],  # No y-scaling for the line brush
            [0, 0, current_brush_radius, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

        row_major_model = np.dot(rm_trans, rm_scale)
        self.model_matrix = row_major_model.T

    def draw(self, view_matrix, projection_matrix):
        if not self.visible or not self.shader_program or not self.VAO:
            return
        glUseProgram(self.shader_program)
        glUniformMatrix4fv(glGetUniformLocation(self.shader_program, "model"), 1, GL_FALSE, self.model_matrix)
        glUniformMatrix4fv(glGetUniformLocation(self.shader_program, "view"), 1, GL_FALSE, view_matrix)
        glUniformMatrix4fv(glGetUniformLocation(self.shader_program, "projection"), 1, GL_FALSE, projection_matrix)
        glUniform4fv(glGetUniformLocation(self.shader_program, "brushColor"), 1, self.color)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glLineWidth(2.0)

        glBindVertexArray(self.VAO)
        glDrawArrays(GL_LINES, 0, len(self.vertices))
        glBindVertexArray(0)

        glLineWidth(1.0)
        glDisable(GL_BLEND)

def get_terrain_height_at_position(terrain_obj, world_x, world_z):
    """Get terrain height at a specific world position."""
    if not terrain_obj or 'vertices' not in terrain_obj:
        return None

    vertices = terrain_obj['vertices']
    if len(vertices) == 0:
        return None

    # For grid-based terrain, use heightmap if available
    terrain_props = terrain_obj.get('terrain_properties')
    if terrain_props:
        heightmap = terrain_props['heightmap']
        resolution = terrain_props['resolution']
        size_x = terrain_props['size_x']
        size_y = terrain_props['size_y']

        # Convert world coordinates to heightmap coordinates
        half_x = size_x / 2.0
        half_y = size_y / 2.0

        if not (-half_x <= world_x <= half_x and -half_y <= world_z <= half_y):
            return None

        vertex_spacing = size_x / (resolution - 1) if resolution > 1 else size_x
        c = int(round((world_x + half_x) / vertex_spacing))
        r = int(round((world_z + half_y) / vertex_spacing))

        if 0 <= r < resolution and 0 <= c < resolution:
            return heightmap[r, c]

    # Fallback: find closest vertex and return its height
    min_dist = float('inf')
    closest_height = None

    for vertex in vertices:
        dist = math.sqrt((vertex[0] - world_x)**2 + (vertex[2] - world_z)**2)
        if dist < min_dist:
            min_dist = dist
            closest_height = vertex[1]

    return closest_height

# --- Helper GLSL Shader Compilation Functions ---
def compile_shader(source, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)
    if not glGetShaderiv(shader, GL_COMPILE_STATUS):
        error_type = "Vertex" if shader_type == GL_VERTEX_SHADER else "Fragment"
        error = glGetShaderInfoLog(shader).decode()
        print(f"ERROR: {error_type} shader compilation error:\n{error}")
        glDeleteShader(shader); raise RuntimeError(f"{error_type} shader compilation failed: {error}")
    return shader

def create_shader_program(vertex_source, fragment_source):
    vertex_shader = compile_shader(vertex_source, GL_VERTEX_SHADER)
    fragment_shader = compile_shader(fragment_source, GL_FRAGMENT_SHADER)
    program = glCreateProgram()
    glAttachShader(program, vertex_shader); glAttachShader(program, fragment_shader)
    glLinkProgram(program)
    if not glGetProgramiv(program, GL_LINK_STATUS):
        error = glGetProgramInfoLog(program).decode()
        print(f"ERROR: Program linking error:\n{error}")
        glDeleteProgram(program); glDeleteShader(vertex_shader); glDeleteShader(fragment_shader)
        raise RuntimeError(f"Shader program linking failed: {error}")
    glDeleteShader(vertex_shader); glDeleteShader(fragment_shader)
    return program

# --- ADD THIS CODE ---

GENERIC_VERTEX_SRC = """#version 330 core
layout(location = 0) in vec3 aPos;
layout(location = 1) in vec3 aNormal;
layout(location = 2) in vec2 aTex;
uniform mat4 model, view, proj;
out vec3 vWorld, vNormal;
out vec2 vUV;
void main(){
    vWorld  = vec3(model * vec4(aPos,1));
    vNormal = mat3(transpose(inverse(model))) * aNormal;
    vUV     = aTex;
    gl_Position = proj * view * vec4(vWorld,1);
}"""

GENERIC_FRAGMENT_SRC = """#version 330 core
in vec3 vWorld, vNormal;
in vec2 vUV;
out vec4 FragCol;
uniform vec3 sunDir, sunCol, horizon, viewPos;
uniform vec4 baseCol;
uniform bool hasTex;
uniform sampler2D tex;
void main(){
    if( baseCol.a < 0.01 ) discard;   // alpha-test – fully invisible
    vec3 N = normalize(vNormal);
    vec3 L = normalize(-sunDir);
    vec3 V = normalize(viewPos - vWorld);
    vec3 R = reflect(-L,N);

    vec3 ambient = horizon * 0.4;
    vec3 diffuse = sunCol * max(0.0, dot(N,L));
    vec3 spec    = sunCol * pow(max(0.0, dot(V,R)), 32) * 0.3;

    vec4 col = baseCol;
    if(hasTex) col *= texture(tex, vUV);

    FragCol = vec4(col.rgb * (ambient + diffuse + spec), col.a);
}"""

# --- Procedural Sky & Clouds GLSL Function Source ---
# (Existing code follows)
PROCEDURAL_SKY_CLOUDS_FUNC_SRC = """

// --- UTILITY FUNCTIONS (Noise Generation) ---

/**
 * @notice A simple pseudo-random number generator (hash function).
 * @param p Input 2D vector.
 * @return A pseudo-random float between 0.0 and 1.0.
 */
float hash(vec2 p) {
    // [FIXED] Using a higher quality hash function (by Inigo Quilez). It produces a more
    // uniformly distributed and less structured pseudo-random value, which is
    // the first step in reducing grid-like artifacts in the final noise.
    vec3 p3  = fract(vec3(p.xyx) * .1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

/**
 * @notice 2D Value Noise function.
 * @dev Generates smooth, continuous noise by interpolating random values at integer grid points.
 * @param st The input coordinate (e.g., UV).
 * @return A noise value between 0.0 and 1.0.
 */
float noise(vec2 st) {
    vec2 i = floor(st); // Integer part of the coordinate
    vec2 f = fract(st); // Fractional part of the coordinate

    // Hermite interpolation (smoothstep) for a smoother transition between cells.
    // This avoids the blocky look of linear interpolation.
    vec2 u = f * f * (3.0 - 2.0 * f);

    // Sample random values at the four corners of the grid cell.
    float a = hash(i + vec2(0.0, 0.0));
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));

    // Bilinearly interpolate the corner values.
    return mix(mix(a, b, u.x), mix(c, d, u.x), u.y);
}

/**
 * @notice Fractal Brownian Motion (FBM).
 * @dev Creates detailed and natural-looking textures by layering multiple octaves of noise
 * at different frequencies and amplitudes.
 * @param st The input coordinate.
 * @param octaves The number of noise layers to combine. More octaves add more detail.
 * @param persistence Controls the decrease in amplitude for each successive octave.
 * @param lacunarity Controls the increase in frequency for each successive octave.
 * @return A normalized FBM value between 0.0 and 1.0.
 */
float fbm(vec2 st, int octaves, float persistence, float lacunarity) {
    float total = 0.0;
    float frequency = 1.0;
    float amplitude = 1.0;
    float maxValue = 0.0; // Used for normalization

    for (int i = 0; i < octaves; i++) {
        total += noise(st * frequency) * amplitude;
        maxValue += amplitude;
        amplitude *= persistence;
        frequency *= lacunarity;
    }

    // Normalize the result to the [0, 1] range to ensure consistent output.
    if (maxValue == 0.0) return 0.0;
    return total / maxValue;
}


// --- APPEARANCE UNIFORMS & CONSTANTS ---

// Sky Colors (now as uniforms)
uniform vec3 u_zenithColor;
uniform vec3 u_horizonColor;
const vec3 SUNSET_COLOR = vec3(0.9, 0.5, 0.2); // Orange/red for sunset

// Sun Properties
const vec3 SUN_COLOR = vec3(1.0, 0.95, 0.85);
const float SUN_DISK_INTENSITY = 40.0; // Higher value = smaller, sharper sun
const float SUN_HAZE_INTENSITY = 0.2;

// Cloud Properties
const float CLOUD_SCALE = 1.2;
const vec2 CLOUD_SCROLL_SPEED = vec2(0.015, 0.008);
const int CLOUD_OCTAVES = 6;
const float CLOUD_PERSISTENCE = 0.48;
const float CLOUD_LACUNARITY = 2.2;
const float CLOUD_COVERAGE = 0.5;
const float CLOUD_SHARPNESS = 0.25;
const float CLOUD_DENSITY = 0.7;
const float CLOUD_WARP_STRENGTH = 0.3;

// Cloud Lighting
const vec3 CLOUD_COLOR_LIGHT = vec3(1.0, 1.0, 1.0);
const vec3 CLOUD_COLOR_DARK_BASE = vec3(0.65, 0.7, 0.75);

// --- MAIN SHADER FUNCTION ---

/**
 * @notice Main function to calculate the final sky and cloud color for a given view direction.
 * @param viewDirWorld The normalized view direction vector from the camera.
 * @param currentTime A float representing time, used for animating the clouds.
 * @param sunDirectionWorld The normalized direction vector pointing towards the sun.
 * @return The final computed RGBA color for the pixel.
 */
vec3 getProceduralSkyAndCloudsColor(vec3 viewDirWorld, float currentTime, vec3 sunDirectionWorld) {

    // --- 1. ATMOSPHERE & SKY GRADIENT ---

    // Calculate sun's elevation. 1.0 at zenith, 0.0 at horizon, -1.0 at nadir.
    float sunElevation = sunDirectionWorld.y;

    // Sunset factor: smoothly transitions from 0 (day) to 1 (sunset) as the sun approaches the horizon.
    float sunsetFactor = smoothstep(0.25, 0.0, sunElevation);

    // Interpolate sky colors based on the sun's elevation.
    vec3 zenithColor = mix(u_zenithColor, SUNSET_COLOR * 0.5, sunsetFactor);
    vec3 horizonColor = mix(u_horizonColor, SUNSET_COLOR * 1.2, sunsetFactor);

    // Calculate the base sky gradient based on the view direction's vertical component.
    float skyGradientFactor = pow(max(0.0, viewDirWorld.y), 0.4);
    vec3 skyColor = mix(horizonColor, zenithColor, skyGradientFactor);


    // --- 2. CLOUD GENERATION ---

    // Project view direction onto a 2D plane for cloud UVs. This mapping reduces distortion
    // at the horizon compared to a simple linear mapping.
    vec2 cloudUV = viewDirWorld.xz / (viewDirWorld.y * 2.0 + 0.5);
    cloudUV *= CLOUD_SCALE;
    cloudUV += currentTime * CLOUD_SCROLL_SPEED; // Animate clouds over time

    // Apply Domain Warping to break up grid artifacts and create more organic shapes.
    // We use two FBM calls with different offsets to create a vector field that displaces the main UVs.
    vec2 warpOffset;
    warpOffset.x = fbm(cloudUV + vec2(1.5, 7.8), 4, 0.5, 2.0); // Use fewer octaves for performance
    warpOffset.y = fbm(cloudUV + vec2(9.2, 3.4), 4, 0.5, 2.0);
    // Remap from [0, 1] to [-1, 1] and scale by strength
    warpOffset = (warpOffset * 2.0 - 1.0) * CLOUD_WARP_STRENGTH;
    vec2 warpedUV = cloudUV + warpOffset;

    // Generate the base cloud noise pattern using the warped UVs.
    float cloudNoise = fbm(warpedUV, CLOUD_OCTAVES, CLOUD_PERSISTENCE, CLOUD_LACUNARITY);

    // Shape the noise into cloud forms using smoothstep to create soft edges.
    float cloudCoverageThreshold = 1.0 - CLOUD_COVERAGE;
    float cloudMap = smoothstep(cloudCoverageThreshold - CLOUD_SHARPNESS, cloudCoverageThreshold + CLOUD_SHARPNESS, cloudNoise);
    cloudMap *= CLOUD_DENSITY;

    // Fade clouds near the horizon for a more realistic sense of distance.
    float horizonFade = smoothstep(0.0, 0.15, viewDirWorld.y);
    cloudMap *= horizonFade;


    // --- 3. LIGHTING ---

    // Calculate how directly the sun is shining towards the camera through the clouds.
    float viewSunDot = max(0.0, dot(viewDirWorld, sunDirectionWorld));

    // Sun Color: Make the sun itself more reddish at sunset.
    vec3 dynamicSunColor = mix(SUN_COLOR, SUNSET_COLOR * 1.5, sunsetFactor);

    // Sun Disk & Haze: Create a bright core and a softer surrounding glow.
    vec3 sunDisk = dynamicSunColor * pow(viewSunDot, SUN_DISK_INTENSITY);
    vec3 sunHaze = dynamicSunColor * pow(viewSunDot, 3.0) * SUN_HAZE_INTENSITY;

    // Cloud Lighting:
    // Base lighting is influenced by the sun's general direction.
    float cloudLightFactor = max(0.0, dot(normalize(vec3(0.0, 1.0, 0.0)), sunDirectionWorld));
    cloudLightFactor = mix(0.5, 1.0, cloudLightFactor);

    // Tint cloud shadows with the ambient sky color for a more integrated look.
    vec3 cloudShadowColor = mix(CLOUD_COLOR_DARK_BASE, skyColor * 0.8, 0.5);
    vec3 cloudColor = mix(cloudShadowColor, CLOUD_COLOR_LIGHT, cloudLightFactor);

    // Add "silver lining" effect where clouds are backlit by the sun.
    cloudColor += dynamicSunColor * pow(viewSunDot, 12.0) * 0.7 * cloudMap;


    // --- 4. COMPOSITION ---

    // Blend the sky and clouds together using the generated cloud map.
    vec3 finalColor = mix(skyColor, cloudColor, cloudMap);

    // Add the sun haze and disk on top of everything.
    finalColor += sunHaze;
    finalColor += sunDisk;

    return finalColor;
}
"""

# --- Terrain Shader Definitions ---
TERRAIN_VERTEX_SHADER_SRC = """
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;
layout (location = 2) in vec2 aTexCoords;
layout (location = 3) in vec3 aBlendWeights;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec3 v_WorldPos;
out vec3 v_Normal;
out vec2 v_TexCoords;
out vec3 v_BlendWeights;

void main() {
    v_WorldPos = vec3(model * vec4(aPos, 1.0));
    v_Normal = mat3(transpose(inverse(model))) * aNormal;
    v_TexCoords = aTexCoords;
    v_BlendWeights = aBlendWeights;
    gl_Position = projection * view * vec4(v_WorldPos, 1.0);
}
"""

TERRAIN_FRAGMENT_SHADER_SRC = """
#version 330 core
out vec4 FragColor;

in vec3 v_WorldPos;
in vec3 v_Normal;
in vec2 v_TexCoords;
in vec3 v_BlendWeights;

// --- Texture Samplers ---
uniform sampler2D texture_slot0;
uniform sampler2D texture_slot1;
uniform sampler2D texture_slot2;

// --- Texture availability flags ---
uniform bool has_texture_slot0;
uniform bool has_texture_slot1;
uniform bool has_texture_slot2;

// --- Fallback colors ---
uniform vec4 color_slot0;
uniform vec4 color_slot1;
uniform vec4 color_slot2;

// --- Lighting & Environment Uniforms ---
uniform vec3 sunDirection_World;
uniform vec3 sunColor;         // NEW: Dynamic color of the sun
uniform vec3 horizonColor;     // NEW: Color of the sky at the horizon for ambient/fog
uniform vec3 viewPos;

// --- Fog Uniforms ---
uniform float fogDensity;      // NEW: Controls how thick the fog is
uniform float fogGradient;     // NEW: Controls how sharply the fog appears with distance

const float TILING_FACTOR = 25.0;

void main() {
    // --- 1. Sample and Blend Textures ---
    vec4 tex_color_0 = has_texture_slot0 ? texture(texture_slot0, v_TexCoords * TILING_FACTOR) : color_slot0;
    vec4 tex_color_1 = has_texture_slot1 ? texture(texture_slot1, v_TexCoords * TILING_FACTOR) : color_slot1;
    vec4 tex_color_2 = has_texture_slot2 ? texture(texture_slot2, v_TexCoords * TILING_FACTOR) : color_slot2;

    vec4 blended_color = tex_color_0 * v_BlendWeights.x +
                         tex_color_1 * v_BlendWeights.y +
                         tex_color_2 * v_BlendWeights.z;

    // --- 2. Dynamic Lighting influenced by the Sky ---
    vec3 norm = normalize(v_Normal);
    vec3 lightDir = normalize(-sunDirection_World);

    // Ambient light is now the sky's horizon color, creating a natural atmospheric fill light.
    float ambientStrength = 0.4;
    vec3 ambient = ambientStrength * horizonColor;

    // Diffuse light uses the dynamic sun color, matching the sunset.
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * sunColor;

    // Specular lighting also uses the sun's color.
    float specularStrength = 0.3;
    vec3 viewDir = normalize(viewPos - v_WorldPos);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);
    vec3 specular = specularStrength * spec * sunColor;

    vec3 final_lighting = ambient + diffuse + specular;
    vec3 lit_color = final_lighting * blended_color.rgb;

    // --- 3. Atmospheric Distance Fog ---
    // The fog fades the terrain to the sky's horizon color based on distance from the camera.
    float distance_from_cam = length(viewPos - v_WorldPos);
    float fogFactor = exp(-pow(distance_from_cam * fogDensity, fogGradient));
    fogFactor = clamp(fogFactor, 0.0, 1.0);

    // Blend the lit terrain color with the fog color (horizon color).
    vec3 final_color = mix(horizonColor, lit_color, fogFactor);

    FragColor = vec4(final_color, blended_color.a);
}
"""

# --- Sky Shader Definitions ---
SKY_VERTEX_SHADER_SRC = """
#version 330 core
layout (location = 0) in vec2 aPos;

uniform mat4 invProjectionMatrix;
uniform mat4 invViewMatrix;

out vec3 v_WorldSpaceViewDir;

void main() {
    vec4 ray_clip = vec4(aPos.x, aPos.y, -1.0, 1.0);
    vec4 ray_eye = invProjectionMatrix * ray_clip;
    ray_eye = vec4(ray_eye.xy, -1.0, 0.0);
    v_WorldSpaceViewDir = mat3(invViewMatrix) * ray_eye.xyz;
    gl_Position = vec4(aPos.x, aPos.y, 0.99999, 1.0);
}
"""

SKY_FRAGMENT_SHADER_SRC = """#version 330 core
out vec4 FragColor;

// --- Inserted Procedural Sky & Clouds Functions ---
""" + PROCEDURAL_SKY_CLOUDS_FUNC_SRC + """
// --- End of Inserted Functions ---

in vec3 v_WorldSpaceViewDir;

uniform float time;
uniform vec3 sunDirection_World;

void main() {
    vec3 viewDir = normalize(v_WorldSpaceViewDir);
    vec3 skyAndCloudColor = getProceduralSkyAndCloudsColor(viewDir, time, sunDirection_World);
    FragColor = vec4(skyAndCloudColor, 1.0);
}
"""

# --- SkyRenderer Class ---
class SkyRenderer:
    def __init__(self):
        self.shader_program = None
        self.VAO = None
        self.VBO = None
        self.quad_vertices = np.array([
            -1.0,  1.0,
            -1.0, -1.0,
             1.0, -1.0,
            -1.0,  1.0,
             1.0, -1.0,
             1.0,  1.0,
        ], dtype=np.float32)

        self._setup_mesh()
        self._setup_shaders()

    def _setup_mesh(self):
        self.VAO = glGenVertexArrays(1)
        glBindVertexArray(self.VAO)
        self.VBO = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, self.quad_vertices.nbytes, self.quad_vertices, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 2 * 4, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def _setup_shaders(self):
        self.shader_program = create_shader_program(SKY_VERTEX_SHADER_SRC, SKY_FRAGMENT_SHADER_SRC)
        self.invProjectionMatrix_loc = glGetUniformLocation(self.shader_program, "invProjectionMatrix")
        self.invViewMatrix_loc = glGetUniformLocation(self.shader_program, "invViewMatrix")
        self.time_loc = glGetUniformLocation(self.shader_program, "time")
        self.sunDirection_loc = glGetUniformLocation(self.shader_program, "sunDirection_World")
        self.zenithColor_loc = glGetUniformLocation(self.shader_program, "u_zenithColor")
        self.horizonColor_loc = glGetUniformLocation(self.shader_program, "u_horizonColor")

    def draw(self, inv_projection_matrix, inv_view_matrix, current_time, sun_direction_world, zenith_color, horizon_color):
        glUseProgram(self.shader_program)
        glUniformMatrix4fv(self.invProjectionMatrix_loc, 1, GL_FALSE, inv_projection_matrix)
        glUniformMatrix4fv(self.invViewMatrix_loc, 1, GL_FALSE, inv_view_matrix)
        glUniform1f(self.time_loc, current_time)
        glUniform3fv(self.sunDirection_loc, 1, sun_direction_world)
        # Pass the colors to the shader
        glUniform3fv(self.zenithColor_loc, 1, zenith_color)
        glUniform3fv(self.horizonColor_loc, 1, horizon_color)

        glBindVertexArray(self.VAO)
        glDrawArrays(GL_TRIANGLES, 0, 6)
        glBindVertexArray(0)
        glUseProgram(0)

class CubeOpenGLFrame(OpenGLFrame):
    def __init__(self, master, app, *args, **kw):
        super().__init__(master, *args, **kw)
        self.app = app # Reference to the main App instance to access UI elements
        self._after_id = None
        self._is_updating_ui = False # Flag to prevent recursive updates

        # FXAA (Fast Approximate Anti-Aliasing) variables
        self.fxaa_enabled = True
        self.fxaa_shader_program = None
        self.fxaa_fbo = None
        self.fxaa_color_texture = None
        self.fxaa_depth_texture = None
        self.fxaa_vao = None
        self.fxaa_vbo = None
        self.screen_width = 800
        self.screen_height = 600

        # --- Camera Attributes ---
        self.camera_pos = np.array([0.0, 1.0, 5.0], dtype=np.float32)
        self.camera_front = np.array([0.0, 0.0, -1.0], dtype=np.float32)
        self.world_up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        self.camera_up = np.copy(self.world_up)
        self.camera_right = np.cross(self.camera_front, self.camera_up)
        
        self.camera_yaw = -90.0
        self.camera_pitch = 0.0

        self.mouse_sensitivity = 0.1
        self.camera_speed = 0.1
        self.last_x = 0
        self.last_y = 0
        self.first_mouse_move = True
        self.rmb_down = False
        self.lmb_down = False  # For terrain editing

        # FPS Controller variables
        self.fps_mouse_sensitivity = None
        self.fps_movement_speed = 5.0
        self.fps_jump_velocity = 0.0
        self.fps_on_ground = True
        self.fps_gravity = -15.0
        self.fps_player_radius = 0.3  # Player collision radius
        self.fps_player_height = 1.8  # Player height

        self.keys_pressed = set()

        # --- Gizmo & Selection Attributes ---
        self.show_world_gizmo = True
        self.gizmo_length = 1.0
        self.selected_part_index = None
        self.gizmo_mode = 'translate' # Modes: 'translate', 'rotate'
        self.active_gizmo_handle = None # e.g., 'X', 'Y', 'Z'
        self.gizmo_handle_meshes = {} # For ray-intersection tests
        self.drag_start_mouse = np.array([0, 0], dtype=np.float32)
        
        # Drag start state now includes decomposed transform components
        self.drag_start_transform = np.eye(4, dtype=np.float32)
        self.drag_start_position = np.zeros(3, dtype=np.float32)
        self.drag_start_rotation = np.zeros(3, dtype=np.float32)
        self.drag_start_scale = np.ones(3, dtype=np.float32)

        self.drag_start_obj_center = np.zeros(3, dtype=np.float32)
        self.drag_plane_normal = np.zeros(3, dtype=np.float32)
        self.drag_plane_point = np.zeros(3, dtype=np.float32)

        # --- Model and Texture Data Structures ---
        self.model_loaded = False
        self.model_draw_list = []
        self.opengl_texture_map = {}
        self.pil_images_awaiting_gl_upload = {}

        # --- Sky Renderer and Time Tracking ---
        self.sky_renderer = None
        self.start_time = 0.0
        self.current_time_gl = 0.0

        # --- Threading Infrastructure ---
        self.thread_pool = ThreadPoolExecutor(max_workers=4, thread_name_prefix="GLFrame")

        # --- Terrain Editing State ---
        self.terrain_editing_mode = False  # When True, terrain editing is active
        self.terrain_brush_size = 25.0     # Brush radius for terrain editing
        self.terrain_brush_strength = 0.5  # Brush strength for terrain editing
        self.current_terrain_obj = None    # Reference to currently selected terrain object
        self.last_mouse_x = 0              # For terrain editing raycasting
        self.last_mouse_y = 0
        self.texture_queue = queue.Queue()
        self.mesh_processing_queue = queue.Queue()
        self.physics_queue = queue.Queue()
        self.loading_lock = threading.Lock()
        self.texture_lock = threading.Lock()
        self.physics_lock = threading.Lock()

        # --- Bind mouse and keyboard events ---
        self.bind("<ButtonPress-1>", self.on_lmb_press)
        self.bind("<ButtonRelease-1>", self.on_lmb_release)
        self.bind("<ButtonPress-3>", self.on_rmb_press)
        self.bind("<ButtonRelease-3>", self.on_rmb_release)
        self.bind("<Motion>", self.on_mouse_move)
        self.bind("<KeyPress>", self.on_key_press)
        self.bind("<KeyRelease>", self.on_key_release)
        self.bind("<FocusIn>", lambda e: self.focus_set())



    def initgl(self):
        print("initgl called")
        glViewport(0, 0, self.width, self.height)
        # Use dynamic sky color from app
        sky_color = self.app.sky_color
        glClearColor(sky_color[0], sky_color[1], sky_color[2], sky_color[3])
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glFrontFace(GL_CCW)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_NORMALIZE)

        # Enable antialiasing
        glEnable(GL_MULTISAMPLE)

        # Setup FXAA anti-aliasing
        self._setup_fxaa()

        # Setup high-quality rendering pipeline
        self._setup_high_quality_rendering()

        # Enable HBAO-like ambient occlusion
        self._setup_hbao()

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, [0.5, 0.5, 1, 0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect_ratio = self.width / self.height if self.width > 0 and self.height > 0 else 1.0
        gluPerspective(45.0, aspect_ratio, 0.1, 2000.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self._update_camera_vectors()

        # Initialize sky renderer
        self.sky_renderer = SkyRenderer()
        self.start_time = time.time()

        # Initialize brush visualizer for terrain editing
        try:
            self.brush_shader = create_shader_program(BRUSH_VERTEX_SHADER, BRUSH_FRAGMENT_SHADER)
            self.brush_visualizer = BrushVisualizer(segments=32)
            self.brush_visualizer.set_shader(self.brush_shader)
            self.brush_visualizer.setup_buffers_gl()
            print("Brush visualizer initialized successfully")
        except Exception as e:
            print(f"Warning: Failed to initialize brush visualizer: {e}")
            self.brush_visualizer = None
            self.brush_shader = None

        # Initialize terrain shader for multi-texture painting
        try:
            self.terrain_shader = create_shader_program(TERRAIN_VERTEX_SHADER_SRC, TERRAIN_FRAGMENT_SHADER_SRC)
            self.terrain_textures = {}  # Dictionary to store terrain texture IDs
            print("Terrain shader initialized successfully")
        except Exception as e:
            print(f"Warning: Failed to initialize terrain shader: {e}")
            self.terrain_shader = None
            self.terrain_textures = {}

        try:
            self.generic_mesh_shader = create_shader_program(GENERIC_VERTEX_SRC, GENERIC_FRAGMENT_SRC)
            self._generic_mesh_locs = {
                'model'   : glGetUniformLocation(self.generic_mesh_shader, "model"),
                'view'    : glGetUniformLocation(self.generic_mesh_shader, "view"),
                'proj'    : glGetUniformLocation(self.generic_mesh_shader, "proj"),
                'sunDir'  : glGetUniformLocation(self.generic_mesh_shader, "sunDir"),
                'sunCol'  : glGetUniformLocation(self.generic_mesh_shader, "sunCol"),
                'horizon' : glGetUniformLocation(self.generic_mesh_shader, "horizon"),
                'viewPos' : glGetUniformLocation(self.generic_mesh_shader, "viewPos"),
                'baseCol' : glGetUniformLocation(self.generic_mesh_shader, "baseCol"),
                'hasTex'  : glGetUniformLocation(self.generic_mesh_shader, "hasTex"),
                'tex'     : glGetUniformLocation(self.generic_mesh_shader, "tex")
            }
            print("Generic mesh shader initialized successfully")
        except Exception as e:
            print(f"Warning: Failed to initialize generic mesh shader: {e}")
            self.generic_mesh_shader = None
            self._generic_mesh_locs = {}

    def _setup_fxaa(self):
        """Setup FXAA (Fast Approximate Anti-Aliasing) using framebuffer objects and post-processing."""
        try:
            # Create FXAA shader program
            self._create_fxaa_shaders()

            # Create framebuffer for FXAA
            self._create_fxaa_framebuffer()

            # Create screen quad for FXAA post-processing
            self._create_fxaa_screen_quad()

            print("FXAA anti-aliasing initialized successfully")

        except Exception as e:
            print(f"Warning: Failed to initialize FXAA: {e}")
            self.fxaa_enabled = False

    def _create_fxaa_shaders(self):
        """Create FXAA vertex and fragment shaders."""
        # FXAA Vertex Shader
        fxaa_vertex_shader = """
        #version 330 core
        layout (location = 0) in vec2 aPos;
        layout (location = 1) in vec2 aTexCoord;

        out vec2 TexCoord;

        void main()
        {
            gl_Position = vec4(aPos.x, aPos.y, 0.0, 1.0);
            TexCoord = aTexCoord;
        }
        """

        # FXAA Fragment Shader
        fxaa_fragment_shader = """
        #version 330 core
        out vec4 FragColor;

        in vec2 TexCoord;

        uniform sampler2D screenTexture;
        uniform vec2 screenSize;

        // FXAA parameters
        const float FXAA_SPAN_MAX = 8.0;
        const float FXAA_REDUCE_MUL = 1.0/8.0;
        const float FXAA_REDUCE_MIN = 1.0/128.0;

        void main()
        {
            vec2 texelStep = 1.0 / screenSize;

            // Sample the center and surrounding pixels
            vec3 rgbNW = texture(screenTexture, TexCoord + vec2(-1.0, -1.0) * texelStep).rgb;
            vec3 rgbNE = texture(screenTexture, TexCoord + vec2(1.0, -1.0) * texelStep).rgb;
            vec3 rgbSW = texture(screenTexture, TexCoord + vec2(-1.0, 1.0) * texelStep).rgb;
            vec3 rgbSE = texture(screenTexture, TexCoord + vec2(1.0, 1.0) * texelStep).rgb;
            vec3 rgbM  = texture(screenTexture, TexCoord).rgb;

            // Convert to luma
            vec3 luma = vec3(0.299, 0.587, 0.114);
            float lumaNW = dot(rgbNW, luma);
            float lumaNE = dot(rgbNE, luma);
            float lumaSW = dot(rgbSW, luma);
            float lumaSE = dot(rgbSE, luma);
            float lumaM  = dot(rgbM,  luma);

            float lumaMin = min(lumaM, min(min(lumaNW, lumaNE), min(lumaSW, lumaSE)));
            float lumaMax = max(lumaM, max(max(lumaNW, lumaNE), max(lumaSW, lumaSE)));

            vec2 dir;
            dir.x = -((lumaNW + lumaNE) - (lumaSW + lumaSE));
            dir.y =  ((lumaNW + lumaSW) - (lumaNE + lumaSE));

            float dirReduce = max((lumaNW + lumaNE + lumaSW + lumaSE) * (0.25 * FXAA_REDUCE_MUL), FXAA_REDUCE_MIN);
            float rcpDirMin = 1.0 / (min(abs(dir.x), abs(dir.y)) + dirReduce);

            dir = min(vec2(FXAA_SPAN_MAX, FXAA_SPAN_MAX),
                      max(vec2(-FXAA_SPAN_MAX, -FXAA_SPAN_MAX),
                          dir * rcpDirMin)) * texelStep;

            vec3 rgbA = 0.5 * (
                texture(screenTexture, TexCoord + dir * (1.0/3.0 - 0.5)).rgb +
                texture(screenTexture, TexCoord + dir * (2.0/3.0 - 0.5)).rgb);
            vec3 rgbB = rgbA * 0.5 + 0.25 * (
                texture(screenTexture, TexCoord + dir * -0.5).rgb +
                texture(screenTexture, TexCoord + dir * 0.5).rgb);

            float lumaB = dot(rgbB, luma);

            if ((lumaB < lumaMin) || (lumaB > lumaMax)) {
                FragColor = vec4(rgbA, 1.0);
            } else {
                FragColor = vec4(rgbB, 1.0);
            }
        }
        """

        # Compile shaders
        self.fxaa_shader_program = create_shader_program(fxaa_vertex_shader, fxaa_fragment_shader)

    def _create_fxaa_framebuffer(self):
        """Create framebuffer for FXAA rendering."""
        # Get current viewport size
        viewport = glGetIntegerv(GL_VIEWPORT)
        self.screen_width = viewport[2]
        self.screen_height = viewport[3]

        # Generate framebuffer
        self.fxaa_fbo = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.fxaa_fbo)

        # Create color texture
        self.fxaa_color_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.fxaa_color_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.screen_width, self.screen_height, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.fxaa_color_texture, 0)

        # Create depth texture
        self.fxaa_depth_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.fxaa_depth_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, self.screen_width, self.screen_height, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self.fxaa_depth_texture, 0)

        # Check framebuffer completeness
        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            raise Exception("FXAA framebuffer not complete")

        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def _create_fxaa_screen_quad(self):
        """Create screen quad for FXAA post-processing."""
        # Screen quad vertices (position and texture coordinates)
        quad_vertices = np.array([
            # positions   # texCoords
            -1.0,  1.0,   0.0, 1.0,
            -1.0, -1.0,   0.0, 0.0,
             1.0, -1.0,   1.0, 0.0,
            -1.0,  1.0,   0.0, 1.0,
             1.0, -1.0,   1.0, 0.0,
             1.0,  1.0,   1.0, 1.0
        ], dtype=np.float32)

        # Generate VAO and VBO
        self.fxaa_vao = glGenVertexArrays(1)
        self.fxaa_vbo = glGenBuffers(1)

        glBindVertexArray(self.fxaa_vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.fxaa_vbo)
        glBufferData(GL_ARRAY_BUFFER, quad_vertices.nbytes, quad_vertices, GL_STATIC_DRAW)

        # Position attribute
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4 * 4, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        # Texture coordinate attribute
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * 4, ctypes.c_void_p(2 * 4))
        glEnableVertexAttribArray(1)

        glBindVertexArray(0)

    def _setup_high_quality_rendering(self):
        """Setup high-quality rendering pipeline from TheHigh V1."""
        # Enhanced lighting setup
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)

        # High-quality sun lighting (from TheHigh V1)
        sun_direction = [0.8, 0.7, -0.6, 0.0]  # Directional light
        sun_color = [1.0, 0.9, 0.7, 1.0]  # Warm sun color
        ambient_color = [0.1, 0.1, 0.1, 1.0]  # Low ambient

        glLightfv(GL_LIGHT0, GL_POSITION, sun_direction)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, sun_color)
        glLightfv(GL_LIGHT0, GL_AMBIENT, ambient_color)
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])  # White specular

        # Enhanced material properties
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        # High-quality rendering settings
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glFrontFace(GL_CCW)

        # Smooth shading for better quality
        glShadeModel(GL_SMOOTH)
        glEnable(GL_NORMALIZE)

        # Enhanced fog for depth (from TheHigh V1)
        glEnable(GL_FOG)
        glFogi(GL_FOG_MODE, GL_EXP2)
        # Use sky color as fog color
        fog_color = self.app.sky_color
        glFogfv(GL_FOG_COLOR, fog_color)
        glFogf(GL_FOG_DENSITY, 0.01)  # Subtle fog
        glFogf(GL_FOG_START, 10.0)
        glFogf(GL_FOG_END, 100.0)

        # High-quality texture filtering
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

        # Enable automatic mipmap generation
        glGenerateMipmap(GL_TEXTURE_2D)

        # Setup shadow system (from TheHigh V1)
        self._setup_shadow_system()

        print("High-quality rendering pipeline initialized")

    def _setup_shadow_system(self):
        """Setup shadow system from TheHigh V1."""
        # Enhanced lighting for shadow casting
        glEnable(GL_LIGHT1)  # Additional light for shadows

        # Shadow casting light (sun direction from TheHigh V1)
        shadow_light_pos = [0.8, 0.7, -0.6, 0.0]  # Directional light
        shadow_light_color = [0.3, 0.3, 0.3, 1.0]  # Shadow color

        glLightfv(GL_LIGHT1, GL_POSITION, shadow_light_pos)
        glLightfv(GL_LIGHT1, GL_DIFFUSE, shadow_light_color)
        glLightfv(GL_LIGHT1, GL_AMBIENT, [0.05, 0.05, 0.05, 1.0])  # Very low ambient for shadows

        # Shadow properties
        self.shadow_intensity = 0.3  # Shadow strength
        self.shadow_softness = 8.0   # Soft shadow edges (from TheHigh V1)

        print("Shadow system initialized")

    def _apply_shadow_calculation(self, part):
        """Apply shadow calculation similar to TheHigh V1."""
        # Get object position
        pos = part['position']

        # Calculate shadow factor based on sun direction
        sun_dir = np.array([0.8, 0.7, -0.6])  # From TheHigh V1
        sun_dir = sun_dir / np.linalg.norm(sun_dir)

        # Simple shadow calculation - objects lower get more shadow
        height_factor = max(0.0, pos[1])  # Height above ground
        shadow_factor = 1.0 - (self.shadow_intensity * (1.0 / (1.0 + height_factor * 0.5)))

        # Apply shadow to ambient lighting
        shadow_ambient = [shadow_factor * 0.1, shadow_factor * 0.1, shadow_factor * 0.1, 1.0]
        glLightfv(GL_LIGHT1, GL_AMBIENT, shadow_ambient)

        return shadow_factor

    def _setup_hbao(self):
        """Setup HBAO-like ambient occlusion using OpenGL lighting."""
        # Enhanced ambient lighting for HBAO effect
        glLightfv(GL_LIGHT1, GL_POSITION, [0.0, 1.0, 0.0, 0.0])  # Directional light from above
        glLightfv(GL_LIGHT1, GL_AMBIENT, [0.15, 0.15, 0.15, 1.0])  # Soft ambient
        glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.3, 0.3, 0.3, 1.0])   # Reduced diffuse for AO effect
        glLightfv(GL_LIGHT1, GL_SPECULAR, [0.1, 0.1, 0.1, 1.0])  # Minimal specular
        glEnable(GL_LIGHT1)

        # Additional directional lights for horizon-based occlusion simulation
        glLightfv(GL_LIGHT2, GL_POSITION, [1.0, 0.0, 0.0, 0.0])  # Side light
        glLightfv(GL_LIGHT2, GL_AMBIENT, [0.05, 0.05, 0.05, 1.0])
        glLightfv(GL_LIGHT2, GL_DIFFUSE, [0.2, 0.2, 0.2, 1.0])
        glEnable(GL_LIGHT2)

        glLightfv(GL_LIGHT3, GL_POSITION, [0.0, 0.0, 1.0, 0.0])  # Front light
        glLightfv(GL_LIGHT3, GL_AMBIENT, [0.05, 0.05, 0.05, 1.0])
        glLightfv(GL_LIGHT3, GL_DIFFUSE, [0.2, 0.2, 0.2, 1.0])
        glEnable(GL_LIGHT3)

        # Global ambient reduction for stronger AO effect
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.1, 0.1, 0.1, 1.0])

    # -------------------------------------------------------------------
    # Camera and Input Handling
    # -------------------------------------------------------------------

    def _update_camera_vectors(self):
        front = np.empty(3, dtype=np.float32)
        front[0] = math.cos(math.radians(self.camera_yaw)) * math.cos(math.radians(self.camera_pitch))
        front[1] = math.sin(math.radians(self.camera_pitch))
        front[2] = math.sin(math.radians(self.camera_yaw)) * math.cos(math.radians(self.camera_pitch))
        self.camera_front = front / np.linalg.norm(front)
        self.camera_right = np.cross(self.camera_front, self.world_up)
        self.camera_right /= np.linalg.norm(self.camera_right)
        self.camera_up = np.cross(self.camera_right, self.camera_front)
        self.camera_up /= np.linalg.norm(self.camera_up)

    def on_lmb_press(self, event):
        self.focus_set()

        # Disable all interactions in FPS mode
        if self.fps_mouse_sensitivity is not None:
            return

        # Track left mouse button state for terrain editing
        self.lmb_down = True

        # Store mouse position for terrain editing
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y

        ray_origin, ray_direction = self._screen_to_world_ray(event.x, event.y)

        # Handle terrain editing mode
        if self.terrain_editing_mode and self.current_terrain_obj:
            self._handle_terrain_editing(ray_origin, ray_direction, event)
            return

        if self.selected_part_index is not None:
            hit_handle, _ = self._get_handle_under_mouse(ray_origin, ray_direction)
            if hit_handle:
                self.active_gizmo_handle = hit_handle
                self._handle_drag_start(event.x, event.y, ray_origin, ray_direction)
                return

        self._update_selection(ray_origin, ray_direction)

    def on_lmb_release(self, event):
        # Track left mouse button state for terrain editing
        self.lmb_down = False

        if self.active_gizmo_handle:
            self._handle_drag_end()

    def on_rmb_press(self, event):
        # In FPS mode, right mouse button is not used for camera
        if self.fps_mouse_sensitivity is not None:
            return

        self.rmb_down = True
        self.first_mouse_move = True
        self.focus_set()

    def on_rmb_release(self, event):
        # In FPS mode, right mouse button is not used for camera
        if self.fps_mouse_sensitivity is not None:
            return

        self.rmb_down = False

    def on_mouse_move(self, event):
        # Store mouse position for brush visualization
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y

        # FPS mode - always capture mouse for looking
        if self.fps_mouse_sensitivity is not None:
            self._handle_fps_mouse_look(event.x, event.y)
            return

        # Handle terrain editing when dragging
        if (self.terrain_editing_mode and self.current_terrain_obj and
            hasattr(self, 'lmb_down') and self.lmb_down):
            ray_origin, ray_direction = self._screen_to_world_ray(event.x, event.y)
            self._handle_terrain_editing(ray_origin, ray_direction, event)
            return

        if self.active_gizmo_handle:
            self._handle_drag_update(event.x, event.y)
            return

        if not self.rmb_down:
            return

        if self.first_mouse_move:
            self.last_x, self.last_y = event.x, event.y
            self.first_mouse_move = False
            return

        x_offset = event.x - self.last_x
        y_offset = self.last_y - event.y
        self.last_x, self.last_y = event.x, event.y

        x_offset *= self.mouse_sensitivity
        y_offset *= self.mouse_sensitivity

        self.camera_yaw += x_offset
        self.camera_pitch = max(-89.0, min(89.0, self.camera_pitch + y_offset))
        self._update_camera_vectors()

    def on_key_press(self, event):
        key = event.keysym.lower()
        self.keys_pressed.add(key)

        # Handle ESC key to exit FPS mode
        if key == 'escape' and self.fps_mouse_sensitivity is not None:
            self.app.toggle_physics()  # Exit FPS mode

    def on_key_release(self, event):
        self.keys_pressed.discard(event.keysym.lower())
        
    def _update_camera_position(self):
        # Check if in FPS mode
        if self.fps_mouse_sensitivity is not None:
            return self._update_fps_movement()

        # Normal free fly camera movement
        speed = self.camera_speed
        # Double speed when shift is pressed
        if 'shift_l' in self.keys_pressed or 'shift_r' in self.keys_pressed:
            speed *= 2.0

        moved = False
        if 'w' in self.keys_pressed:
            self.camera_pos += self.camera_front * speed
            moved = True
        if 's' in self.keys_pressed:
            self.camera_pos -= self.camera_front * speed
            moved = True
        if 'a' in self.keys_pressed:
            self.camera_pos -= self.camera_right * speed
            moved = True
        if 'd' in self.keys_pressed:
            self.camera_pos += self.camera_right * speed
            moved = True
        if 'space' in self.keys_pressed:
            self.camera_pos += self.world_up * speed
            moved = True
        return moved

    def _update_fps_movement(self):
        """CS:GO-style FPS movement with gravity and jumping."""
        dt = 0.016  # Assume 60 FPS
        moved = False

        # Ground movement speed
        move_speed = self.fps_movement_speed * dt

        # Handle jumping
        if 'space' in self.keys_pressed and self.fps_on_ground:
            self.fps_jump_velocity = 8.0  # CS:GO-like jump strength
            self.fps_on_ground = False
            moved = True

        # Apply gravity
        if not self.fps_on_ground:
            self.fps_jump_velocity += self.fps_gravity * dt
            new_y = self.camera_pos[1] + self.fps_jump_velocity * dt

            # Check for collision with objects above/below
            test_pos = np.array([self.camera_pos[0], new_y, self.camera_pos[2]])

            # Ground collision (Y = 1.8 is eye level, so ground is at Y = 0)
            ground_level = self._get_ground_level_at_position(self.camera_pos)

            if new_y <= ground_level:
                self.camera_pos[1] = ground_level
                self.fps_jump_velocity = 0.0
                self.fps_on_ground = True
            else:
                self.camera_pos[1] = new_y
            moved = True

        # Horizontal movement (CS:GO style - no flying)
        movement_vector = np.array([0.0, 0.0, 0.0], dtype=np.float32)

        if 'w' in self.keys_pressed:
            # Move forward on XZ plane only
            forward_xz = np.array([self.camera_front[0], 0.0, self.camera_front[2]], dtype=np.float32)
            forward_xz = forward_xz / (np.linalg.norm(forward_xz) + 1e-6)
            movement_vector += forward_xz * move_speed
            moved = True

        if 's' in self.keys_pressed:
            # Move backward on XZ plane only
            forward_xz = np.array([self.camera_front[0], 0.0, self.camera_front[2]], dtype=np.float32)
            forward_xz = forward_xz / (np.linalg.norm(forward_xz) + 1e-6)
            movement_vector -= forward_xz * move_speed
            moved = True

        if 'a' in self.keys_pressed:
            # Strafe left
            movement_vector -= self.camera_right * move_speed
            moved = True

        if 'd' in self.keys_pressed:
            # Strafe right
            movement_vector += self.camera_right * move_speed
            moved = True

        # Apply movement with collision detection
        if np.linalg.norm(movement_vector) > 0:
            new_position = self.camera_pos + movement_vector
            # Check collision with physics objects
            if not self._check_player_collision(new_position):
                self.camera_pos = new_position
            else:
                # Try sliding along walls
                self._handle_player_sliding(movement_vector)

        return moved

    def _handle_fps_mouse_look(self, mouse_x, mouse_y):
        """Handle smooth mouse look for FPS mode with locked mouse."""
        if not hasattr(self, 'fps_mouse_locked') or not self.fps_mouse_locked:
            return

        # Calculate center of frame
        center_x = self.winfo_width() // 2
        center_y = self.winfo_height() // 2

        # Calculate offset from center
        x_offset = mouse_x - center_x
        y_offset = center_y - mouse_y  # Reversed since y-coordinates go from bottom to top

        # Only process if there's significant movement to avoid jitter
        if abs(x_offset) < 2 and abs(y_offset) < 2:
            return

        # Apply sensitivity
        sensitivity = self.fps_mouse_sensitivity
        x_offset *= sensitivity
        y_offset *= sensitivity

        # Update yaw and pitch
        self.camera_yaw += x_offset
        self.camera_pitch += y_offset

        # Constrain pitch (CS:GO style - can't look too far up/down)
        if self.camera_pitch > 89.0:
            self.camera_pitch = 89.0
        if self.camera_pitch < -89.0:
            self.camera_pitch = -89.0

        # Update camera vectors
        self._update_camera_vectors()

        # Warp mouse back to center to keep it locked
        self.after_idle(self._warp_mouse_to_center)

    def _init_fps_mouse_lock(self):
        """Initialize mouse locking for FPS mode."""
        # Hide cursor
        self.configure(cursor="none")

        # Get center of the OpenGL frame
        self.center_x = self.winfo_width() // 2
        self.center_y = self.winfo_height() // 2

        # Initialize mouse position tracking
        self.fps_mouse_locked = True
        self.first_mouse_move = True

        # Warp mouse to center initially
        self.after(10, self._warp_mouse_to_center)

        print("Mouse locked and hidden for FPS mode")

    def _exit_fps_mouse_lock(self):
        """Exit mouse locking and restore cursor."""
        # Show cursor
        self.configure(cursor="")

        # Reset mouse tracking
        self.fps_mouse_locked = False
        self.first_mouse_move = True

        print("Mouse unlocked and cursor restored")

    def _warp_mouse_to_center(self):
        """Warp mouse to center of the frame."""
        if hasattr(self, 'fps_mouse_locked') and self.fps_mouse_locked:
            try:
                # Get absolute position of the frame center
                abs_x = self.winfo_rootx() + self.center_x
                abs_y = self.winfo_rooty() + self.center_y

                # Warp mouse to center
                self.event_generate('<Motion>', warp=True, x=self.center_x, y=self.center_y)

                # Update last known position to center
                self.last_x = self.center_x
                self.last_y = self.center_y
            except Exception as e:
                print(f"Mouse warp error: {e}")

    def _check_player_collision(self, new_position):
        """Check if player would collide with physics objects at new position."""
        if not hasattr(self.app, 'physics_objects'):
            return False

        player_radius = self.fps_player_radius
        player_height = self.fps_player_height

        # Player bounding cylinder
        player_bottom = new_position[1] - player_height
        player_top = new_position[1]
        player_center_xz = np.array([new_position[0], new_position[2]])

        # Check collision with each physics object
        for physics_obj in self.app.physics_objects:
            if physics_obj['type'] == 'None':
                continue

            obj_bounds = physics_obj['bounds']
            obj_pos = physics_obj['position']

            # Check Y overlap first (height collision)
            if player_bottom > obj_bounds['max'][1] or player_top < obj_bounds['min'][1]:
                continue  # No vertical overlap

            # Check XZ collision based on object shape
            if self._check_xz_collision(player_center_xz, player_radius, physics_obj):
                # Apply player interaction force to rigid body objects (but not static)
                if physics_obj['type'] == 'RigidBody':
                    self._apply_player_push_force(physics_obj, new_position)
                # Both Static and RigidBody objects block player movement
                return True  # Collision detected

        return False  # No collision

    def _check_xz_collision(self, player_center_xz, player_radius, physics_obj):
        """Check XZ plane collision between player and physics object with proper transforms."""
        obj_bounds = physics_obj['bounds']
        obj_pos = physics_obj['position']
        shape = obj_bounds['shape']
        rotation = obj_bounds.get('rotation', np.array([0, 0, 0]))

        obj_center_xz = np.array([obj_pos[0], obj_pos[2]])

        if shape == 'Sphere':
            # Sphere collision (rotation doesn't affect sphere)
            obj_radius = obj_bounds.get('radius', np.max(obj_bounds['size']) * 0.5)
            distance = np.linalg.norm(player_center_xz - obj_center_xz)
            return distance < (player_radius + obj_radius)

        elif shape == 'Cylinder' or shape == 'Capsule':
            # Cylinder collision - check if rotated
            obj_radius = obj_bounds.get('radius', max(obj_bounds['size'][0], obj_bounds['size'][2]) * 0.5)

            # If cylinder is rotated significantly, treat as oriented bounding box
            if abs(rotation[0]) > 0.1 or abs(rotation[2]) > 0.1:
                return self._check_oriented_box_collision(player_center_xz, player_radius, physics_obj)
            else:
                # Standard cylinder collision
                distance = np.linalg.norm(player_center_xz - obj_center_xz)
                return distance < (player_radius + obj_radius)

        else:
            # Box collision (Cube, Mesh, Cone, etc.) - check for rotation
            if np.any(np.abs(rotation) > 0.01):
                # Rotated box - use oriented bounding box collision
                return self._check_oriented_box_collision(player_center_xz, player_radius, physics_obj)
            else:
                # Axis-aligned box collision
                expanded_min = obj_bounds['min'][[0, 2]] - player_radius
                expanded_max = obj_bounds['max'][[0, 2]] + player_radius

                return (player_center_xz[0] >= expanded_min[0] and
                        player_center_xz[0] <= expanded_max[0] and
                        player_center_xz[1] >= expanded_min[1] and
                        player_center_xz[1] <= expanded_max[1])

    def _check_oriented_box_collision(self, player_center_xz, player_radius, physics_obj):
        """Check collision with rotated/oriented bounding box."""
        obj_bounds = physics_obj['bounds']
        obj_pos = physics_obj['position']
        rotation = obj_bounds.get('rotation', np.array([0, 0, 0]))
        scale = obj_bounds.get('scale', np.array([1, 1, 1]))

        # Transform player position to object's local space
        obj_center_3d = np.array([obj_pos[0], 0, obj_pos[2]])
        player_3d = np.array([player_center_xz[0], 0, player_center_xz[1]])

        # Create inverse rotation matrix (only Y rotation for XZ plane)
        cos_y, sin_y = np.cos(-rotation[1]), np.sin(-rotation[1])
        inv_rot_y = np.array([
            [cos_y, 0, sin_y],
            [0, 1, 0],
            [-sin_y, 0, cos_y]
        ])

        # Transform to local space
        local_player = inv_rot_y @ (player_3d - obj_center_3d)
        local_player_xz = np.array([local_player[0], local_player[2]])

        # Get original object size before scaling
        original_vertices = physics_obj.get('original_vertices', obj_bounds.get('mesh_vertices', np.array([[0,0,0]])))
        if len(original_vertices) > 0:
            original_size = np.max(original_vertices, axis=0) - np.min(original_vertices, axis=0)
        else:
            original_size = np.array([2, 2, 2])  # Default size

        # Apply scale to get local bounding box
        local_half_size = (original_size[[0, 2]] * scale[[0, 2]]) * 0.5

        # Check collision in local space
        expanded_half_size = local_half_size + player_radius

        return (abs(local_player_xz[0]) <= expanded_half_size[0] and
                abs(local_player_xz[1]) <= expanded_half_size[1])

    def _handle_player_sliding(self, movement_vector):
        """Handle player sliding along walls when collision occurs."""
        # Try moving only in X direction
        x_movement = np.array([movement_vector[0], 0.0, 0.0])
        if np.linalg.norm(x_movement) > 0:
            new_pos_x = self.camera_pos + x_movement
            if not self._check_player_collision(new_pos_x):
                self.camera_pos = new_pos_x
                return

        # Try moving only in Z direction
        z_movement = np.array([0.0, 0.0, movement_vector[2]])
        if np.linalg.norm(z_movement) > 0:
            new_pos_z = self.camera_pos + z_movement
            if not self._check_player_collision(new_pos_z):
                self.camera_pos = new_pos_z
                return

    def _apply_player_push_force(self, physics_obj, player_pos):
        """Apply force to physics objects when player walks into them."""
        obj_pos = physics_obj['position']
        player_center_xz = np.array([player_pos[0], player_pos[2]])
        obj_center_xz = np.array([obj_pos[0], obj_pos[2]])

        # Calculate push direction (from player to object)
        push_direction = obj_center_xz - player_center_xz
        distance = np.linalg.norm(push_direction)

        if distance > 0.001:  # Avoid division by zero
            push_direction = push_direction / distance

            # Calculate push force based on object mass and player movement
            obj_mass = physics_obj['mass']
            player_mass = 70.0  # Average human mass in kg

            # Lighter objects get pushed more easily
            push_strength = min(2.0, player_mass / (obj_mass + 1.0))

            # Apply horizontal force
            force_3d = np.array([push_direction[0], 0.0, push_direction[1]]) * push_strength * 0.1
            physics_obj['velocity'] += force_3d

            # Add slight upward force for realism (objects can be lifted slightly)
            if obj_mass < 5.0:  # Only light objects
                physics_obj['velocity'][1] += 0.05

            # Add angular velocity for realistic tumbling
            physics_obj['angular_velocity'][1] += (np.random.random() - 0.5) * 0.2

    def _get_ground_level_at_position(self, position):
        """Get the ground level at a specific XZ position, considering physics objects."""
        base_ground = 1.8  # Default eye level height
        highest_ground = base_ground

        if not hasattr(self.app, 'physics_objects'):
            return base_ground

        player_xz = np.array([position[0], position[2]])
        player_radius = self.fps_player_radius

        # Check all static physics objects that could act as ground
        for physics_obj in self.app.physics_objects:
            if physics_obj['type'] != 'Static':
                continue  # Only static objects can be stood on

            obj_bounds = physics_obj['bounds']
            obj_pos = physics_obj['position']

            # Check if player is above this object
            if position[1] > obj_bounds['max'][1]:
                # Check XZ overlap
                if self._check_xz_collision(player_xz, player_radius, physics_obj):
                    # Player is standing on this object
                    object_top = obj_bounds['max'][1] + self.fps_player_height
                    highest_ground = max(highest_ground, object_top)

        return highest_ground

    # -------------------------------------------------------------------
    # Terrain Editing Methods
    # -------------------------------------------------------------------

    def _handle_terrain_editing(self, ray_origin, ray_direction, event):
        """Handle terrain editing - sculpting or painting based on current mode."""
        if not self.current_terrain_obj:
            return

        # Find intersection with terrain
        intersection_point = ray_terrain_intersection(ray_origin, ray_direction, self.current_terrain_obj)
        if intersection_point is None:
            return

        # Get current terrain tool mode
        current_mode = getattr(self.app, 'terrain_tool_mode_var', None)
        if current_mode is None:
            return

        mode = current_mode.get()

        # Handle different modes
        if mode == "Paint":
            # PAINT MODE: Paint terrain, Shift+click removes paint
            is_removing = False
            if hasattr(event, 'state') and (event.state & 0x1):  # Shift key
                is_removing = True
            self._paint_terrain_at_point(intersection_point, is_removing)

        elif mode in ["Sculpt", "Smooth"]:
            # SCULPT MODE: Sculpt terrain, Shift+click lowers
            is_raising = True
            if hasattr(event, 'state') and (event.state & 0x1):  # Shift key
                is_raising = False
            self._modify_terrain_at_point(intersection_point, is_raising)

    def _modify_terrain_at_point(self, world_point, is_raising=True):
        """Modify terrain height at a specific world point using proper sculpting."""
        if not self.current_terrain_obj or not self.current_terrain_obj.get('is_terrain', False):
            return

        # Get terrain properties
        terrain_props = self.current_terrain_obj.get('terrain_properties')
        if not terrain_props:
            return

        vertices = self.current_terrain_obj['vertices']
        heightmap = terrain_props['heightmap']
        resolution = terrain_props['resolution']
        size_x = terrain_props['size_x']
        size_y = terrain_props['size_y']

        # Apply sculpting using the same algorithm as GroundController.py
        direction = 1 if is_raising else -1
        changed = self._sculpt_terrain_vertices(
            world_point[0], world_point[2],
            self.terrain_brush_size,
            self.terrain_brush_strength,
            direction,
            vertices, heightmap, resolution, size_x, size_y
        )

        if changed:
            # Update the terrain object
            self.current_terrain_obj['vertices'] = vertices
            terrain_props['heightmap'] = heightmap

            # Recalculate normals
            self._recalculate_terrain_normals()

    def _sculpt_terrain_vertices(self, world_x, world_z, radius, strength, direction,
                                vertices, heightmap, resolution, size_x, size_y):
        """Sculpt terrain vertices using the same algorithm as GroundController.py"""
        if vertices.size == 0:
            return False

        radius_sq = radius * radius
        changed_geometry = False
        vertex_spacing = size_x / (resolution - 1) if resolution > 1 else size_x
        half_size_x = size_x / 2.0
        half_size_y = size_y / 2.0

        # Store height updates to avoid feedback loop
        new_heights_updates = {}

        for i in range(vertices.shape[0]):
            vx, vz = vertices[i, 0], vertices[i, 2]
            dist_sq = (vx - world_x)**2 + (vz - world_z)**2

            if dist_sq < radius_sq:
                falloff = max(0, 1.0 - math.sqrt(dist_sq) / radius if radius > 1e-5 else 1.0)
                current_y = vertices[i, 1]
                new_y = current_y + direction * strength * falloff
                new_heights_updates[i] = new_y
                changed_geometry = True

        if changed_geometry:
            # Apply height updates
            for i, new_y in new_heights_updates.items():
                vertices[i, 1] = new_y

                # Update heightmap
                vx, vz = vertices[i, 0], vertices[i, 2]
                c = int(round((vx + half_size_x) / vertex_spacing))
                r = int(round((vz + half_size_y) / vertex_spacing))
                if 0 <= r < resolution and 0 <= c < resolution:
                    heightmap[r, c] = new_y

        return changed_geometry

    def _recalculate_terrain_normals(self):
        """Recalculate terrain normals after sculpting."""
        if not self.current_terrain_obj:
            return

        vertices = self.current_terrain_obj['vertices']
        # This is a simplified normal calculation. For better results, a per-face
        # normal calculation followed by averaging for each vertex is needed.
        # However, for basic lighting this is sufficient.
        temp_mesh = trimesh.Trimesh(vertices=vertices, faces=self.current_terrain_obj['faces'])
        temp_mesh.fix_normals()

        self.current_terrain_obj['normals'] = np.array(temp_mesh.vertex_normals, dtype=np.float32)

        # CRITICAL FIX: Update the geometry VBOs on the GPU
        self._update_terrain_geometry_vbos(self.current_terrain_obj)

    def _update_terrain_geometry_vbos(self, terrain_obj):
        """Update terrain geometry VBOs after sculpting changes."""
        if not terrain_obj or terrain_obj.get('VAO') is None:
            return

        try:
            # Update vertex positions (VBO index 0)
            glBindBuffer(GL_ARRAY_BUFFER, terrain_obj['VBOs'][0])
            glBufferSubData(GL_ARRAY_BUFFER, 0, terrain_obj['vertices'].nbytes, terrain_obj['vertices'])

            # Update normals (VBO index 1)
            glBindBuffer(GL_ARRAY_BUFFER, terrain_obj['VBOs'][1])
            glBufferSubData(GL_ARRAY_BUFFER, 0, terrain_obj['normals'].nbytes, terrain_obj['normals'])

            glBindBuffer(GL_ARRAY_BUFFER, 0)

        except Exception as e:
            print(f"Error updating terrain geometry VBOs: {e}")

    def set_terrain_editing_mode(self, enabled, terrain_obj=None):
        """Enable or disable terrain editing mode."""
        self.terrain_editing_mode = enabled
        if enabled and terrain_obj:
            self.current_terrain_obj = terrain_obj
        elif not enabled:
            self.current_terrain_obj = None

    def set_terrain_brush_size(self, size):
        """Set the terrain brush size."""
        self.terrain_brush_size = max(1.0, min(100.0, size))

    def set_terrain_brush_strength(self, strength):
        """Set the terrain brush strength."""
        self.terrain_brush_strength = max(0.1, min(2.0, strength))

    def set_terrain_texture(self, slot_index, pil_image):
        """Set terrain texture for a specific slot."""
        if not (0 <= slot_index < 3):
            print(f"Invalid slot index: {slot_index}")
            return

        try:
            # Clear existing texture if any
            if slot_index in self.terrain_textures:
                glDeleteTextures(1, [self.terrain_textures[slot_index]])
                del self.terrain_textures[slot_index]

            if pil_image is None:
                print(f"Cleared texture for slot {slot_index + 1}")
                return

            # Convert PIL image to OpenGL texture
            img_data = pil_image.convert("RGBA")
            img_width, img_height = img_data.size
            img_bytes = img_data.tobytes()

            # Generate OpenGL texture
            texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img_width, img_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_bytes)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glBindTexture(GL_TEXTURE_2D, 0)

            # Store texture ID for rendering
            self.terrain_textures[slot_index] = texture_id

            print(f"Loaded texture for slot {slot_index + 1}: {img_width}x{img_height}")

        except Exception as e:
            print(f"Error setting terrain texture: {e}")

    def _setup_terrain_buffers(self, part):
        """Creates VAO and VBOs for a terrain object for shader-based rendering."""
        if part.get('VAO') is not None: # Buffers already created
            glDeleteVertexArrays(1, [part['VAO']])
            if part.get('VBOs'):
                glDeleteBuffers(len(part['VBOs']), part['VBOs'])

        terrain_props = part.get('terrain_properties', {})
        if 'blend_weights' not in terrain_props:
            return # Not a valid terrain object

        VAO = glGenVertexArrays(1)
        glBindVertexArray(VAO)

        # 1. Vertex Buffer
        VBO_verts = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, VBO_verts)
        glBufferData(GL_ARRAY_BUFFER, part['vertices'].nbytes, part['vertices'], GL_DYNAMIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)

        # 2. Normals Buffer
        VBO_normals = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, VBO_normals)
        glBufferData(GL_ARRAY_BUFFER, part['normals'].nbytes, part['normals'], GL_DYNAMIC_DRAW)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(1)

        # 3. TexCoords Buffer
        VBO_texcoords = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, VBO_texcoords)
        glBufferData(GL_ARRAY_BUFFER, part['texcoords'].nbytes, part['texcoords'], GL_STATIC_DRAW)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(2)

        # 4. BlendWeights Buffer
        VBO_blend_weights = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, VBO_blend_weights)
        glBufferData(GL_ARRAY_BUFFER, terrain_props['blend_weights'].nbytes, terrain_props['blend_weights'], GL_DYNAMIC_DRAW)
        glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(3)

        # 5. Index Buffer (EBO)
        EBO = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, part['faces'].nbytes, part['faces'], GL_STATIC_DRAW)

        # Unbind VAO
        glBindVertexArray(0)

        # Store buffer IDs in the part dictionary for later use
        part['VAO'] = VAO
        part['VBOs'] = [VBO_verts, VBO_normals, VBO_texcoords, VBO_blend_weights, EBO]
        print(f"Initialized shader buffers for terrain: {part['name']}")

    def _setup_mesh_buffers(self, part):
        if part.get('VAO') is not None:
            return
        VAO = glGenVertexArrays(1)
        glBindVertexArray(VAO)

        # 1. vertices
        vbo_v = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo_v)
        glBufferData(GL_ARRAY_BUFFER, part['vertices'].nbytes, part['vertices'], GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)

        # 2. normals
        vbo_n = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo_n)
        glBufferData(GL_ARRAY_BUFFER, part['normals'].nbytes, part['normals'], GL_STATIC_DRAW)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(1)

        vbo_t = None
        # 3. texcoords (ONLY if they exist)
        if part.get('texcoords') is not None:
            vbo_t = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, vbo_t)
            glBufferData(GL_ARRAY_BUFFER, part['texcoords'].nbytes, part['texcoords'], GL_STATIC_DRAW)
            glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 0, None)
            glEnableVertexAttribArray(2)

        # 4. indices
        ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, part['faces'].nbytes, part['faces'], GL_STATIC_DRAW)

        glBindVertexArray(0)

        part['VAO']  = VAO
        part['VBOs'] = [vbo_v, vbo_n, vbo_t, ebo]

    def _paint_terrain_at_point(self, world_point, is_removing=False):
        if not self.current_terrain_obj or not self.current_terrain_obj.get('is_terrain', False):
            return

        terrain_props = self.current_terrain_obj.get('terrain_properties')
        if not terrain_props or 'blend_weights' not in terrain_props:
            return

        vertices = self.current_terrain_obj['vertices']
        blend_weights = terrain_props['blend_weights']
        active_slot = self.app.active_texture_slot.get()

        paint_strength = self.app.paint_strength_var.get()
        radius = self.app.brush_size_var.get()
        radius_sq = radius * radius
        changed_weights = False

        for i in range(vertices.shape[0]):
            vx, vz = vertices[i, 0], vertices[i, 2]
            dist_sq = (vx - world_point[0])**2 + (vz - world_point[2])**2
            if dist_sq < radius_sq:
                falloff = 1.0 - math.sqrt(dist_sq) / radius
                paint_amount = paint_strength * falloff

                current_weights = blend_weights[i]

                if is_removing:
                    current_weights[active_slot] -= paint_amount
                else:
                    current_weights[active_slot] += paint_amount

                # Ensure weights don't go below 0
                current_weights = np.maximum(current_weights, 0)

                total_weight = np.sum(current_weights)
                if total_weight > 1e-6:
                    blend_weights[i] = current_weights / total_weight

                changed_weights = True

        if changed_weights:
            self._update_terrain_blend_weights(self.current_terrain_obj)

    def _update_terrain_blend_weights(self, terrain_obj):
        """Update terrain VAO with new blend weights after painting."""
        if not terrain_obj or terrain_obj.get('VAO') is None:
            return

        try:
            terrain_props = terrain_obj.get('terrain_properties', {})
            blend_weights = terrain_props.get('blend_weights')

            if blend_weights is None:
                return

            # Update blend weights VBO (VBO index 3)
            glBindBuffer(GL_ARRAY_BUFFER, terrain_obj['VBOs'][3])
            glBufferSubData(GL_ARRAY_BUFFER, 0, blend_weights.nbytes, blend_weights)
            glBindBuffer(GL_ARRAY_BUFFER, 0)

        except Exception as e:
            print(f"Error updating terrain blend weights: {e}")

    # -------------------------------------------------------------------
    # Model Loading and Processing
    # -------------------------------------------------------------------
    
    def _recompose_transform(self, part):
        """Computes the world transform matrix from position, rotation, and scale."""
        pos = part.get('position', [0,0,0])
        rot = part.get('rotation', [0,0,0]) # Euler angles in radians
        sca = part.get('scale', [1,1,1])
        # Using trimesh to compose the matrix, 'sxyz' is a common Euler order.
        return trimesh.transformations.compose_matrix(scale=sca, angles=rot, translate=pos)

    def _cleanup_old_model_resources(self):
        self.model_draw_list.clear()
        self.selected_part_index = None
        self._update_properties_panel() # Update UI to reflect no selection
        try:
            glGetString(GL_VERSION)
            for tex_id in self.opengl_texture_map.values():
                if tex_id != 0: glDeleteTextures([tex_id])
        except Exception as e:
            print(f"Warning: No GL context during final cleanup: {e}")
        self.opengl_texture_map.clear()
        self.pil_images_awaiting_gl_upload.clear() 
        self.model_loaded = False

    def _generate_gl_texture_for_image(self, pil_image_obj):
        try:
            img = pil_image_obj.convert("RGBA")
            img_data = img.tobytes("raw", "RGBA", 0, -1)
            width, height = img.size
            gl_tex_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, gl_tex_id)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
            glGenerateMipmap(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, 0)
            return gl_tex_id
        except Exception as e:
            print(f"Error creating OpenGL texture: {e}")
            return 0

    def _prepare_texture_data_threaded(self, img_id, pil_img):
        """Prepare texture data in background thread (CPU-only operations)."""
        try:
            img = pil_img.convert("RGBA")
            img_data = img.tobytes("raw", "RGBA", 0, -1)
            width, height = img.size
            return {
                'img_id': img_id,
                'img_data': img_data,
                'width': width,
                'height': height,
                'success': True
            }
        except Exception as e:
            print(f"Error preparing texture data: {e}")
            return {'img_id': img_id, 'success': False, 'error': str(e)}

    def _create_and_cache_missing_gl_textures(self):
        if not self.pil_images_awaiting_gl_upload:
            # Process any completed texture preparations
            self._process_completed_texture_preparations()
            return

        images_to_process = list(self.pil_images_awaiting_gl_upload.items())
        self.pil_images_awaiting_gl_upload.clear()

        # Submit texture preparation tasks to thread pool
        with self.texture_lock:
            for img_id, pil_img in images_to_process:
                if img_id not in self.opengl_texture_map:
                    # Submit CPU-intensive texture preparation to thread pool
                    future = self.thread_pool.submit(self._prepare_texture_data_threaded, img_id, pil_img)
                    self.texture_queue.put(future)

        # Process any completed texture preparations
        self._process_completed_texture_preparations()

    def _process_completed_texture_preparations(self):
        """Process completed texture preparation tasks and create OpenGL textures."""
        completed_textures = []

        # Check for completed texture preparation tasks
        while not self.texture_queue.empty():
            try:
                future = self.texture_queue.get_nowait()
                if future.done():
                    completed_textures.append(future)
                else:
                    # Put back if not done
                    self.texture_queue.put(future)
                    break
            except queue.Empty:
                break

        # Create OpenGL textures for completed preparations
        for future in completed_textures:
            try:
                texture_data = future.result()
                if texture_data['success']:
                    img_id = texture_data['img_id']
                    if img_id not in self.opengl_texture_map:
                        # Create OpenGL texture (must be done on main thread)
                        gl_tex_id = glGenTextures(1)
                        glBindTexture(GL_TEXTURE_2D, gl_tex_id)
                        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
                        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
                                   texture_data['width'], texture_data['height'],
                                   0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data['img_data'])
                        glGenerateMipmap(GL_TEXTURE_2D)
                        glBindTexture(GL_TEXTURE_2D, 0)
                        self.opengl_texture_map[img_id] = gl_tex_id
                else:
                    print(f"Texture preparation failed: {texture_data.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"Error processing completed texture: {e}")

    def _process_mesh_normals_threaded(self, mesh_obj):
        """Process mesh normals in background thread."""
        try:
            if not hasattr(mesh_obj, 'vertex_normals') or len(mesh_obj.vertex_normals) != len(mesh_obj.vertices):
                mesh_obj.fix_normals()
            return mesh_obj
        except Exception as e:
            print(f"Error processing mesh normals: {e}")
            return mesh_obj

    def _calculate_rigidbody_physics_threaded(self, physics_obj, dt):
        """Calculate rigidbody physics in background thread."""
        try:
            # Create a copy to avoid thread safety issues
            obj_copy = {
                'position': physics_obj['position'].copy(),
                'velocity': physics_obj['velocity'].copy(),
                'angular_velocity': physics_obj['angular_velocity'].copy(),
                'mass': physics_obj['mass'],
                'stability_factor': physics_obj['stability_factor'],
                'bounds': physics_obj['bounds'].copy()
            }

            # Apply gravity scaled by mass
            gravity_force = obj_copy['mass'] * 9.81
            obj_copy['velocity'][1] -= gravity_force * dt

            # Apply velocity damping (air resistance)
            damping = 0.98
            obj_copy['velocity'] *= damping
            obj_copy['angular_velocity'] *= damping

            # Update position
            obj_copy['position'] += obj_copy['velocity'] * dt

            # Ground collision check
            ground_level = 0.0
            if obj_copy['position'][1] <= ground_level:
                obj_copy['position'][1] = ground_level
                obj_copy['velocity'][1] = 0.0

                # Add some bounce for realism
                if abs(obj_copy['velocity'][1]) > 0.1:
                    obj_copy['velocity'][1] = -obj_copy['velocity'][1] * 0.3

            return {
                'position': obj_copy['position'],
                'velocity': obj_copy['velocity'],
                'angular_velocity': obj_copy['angular_velocity']
            }
        except Exception as e:
            print(f"Error in threaded physics calculation: {e}")
            return None

    def _calculate_inverse_matrices(self, projection_matrix, view_matrix):
        """Calculate inverse matrices in background thread."""
        try:
            inv_projection = np.linalg.inv(projection_matrix)
            inv_view = np.linalg.inv(view_matrix)
            return inv_projection, inv_view
        except np.linalg.LinAlgError as e:
            print(f"Matrix inversion error in thread: {e}")
            raise

    def _process_mesh_for_drawing(self, mesh_obj, world_transform, geom_name_hint="mesh_part"):
        if not hasattr(mesh_obj, 'vertices') or len(mesh_obj.vertices) == 0: return

        if hasattr(mesh_obj, 'faces') and mesh_obj.faces.shape[1] == 4:
            mesh_obj = mesh_obj.subdivide_to_size(max_edge=1e9)

        if not hasattr(mesh_obj, 'faces') or mesh_obj.faces.shape[1] != 3: return

        future = self.thread_pool.submit(self._process_mesh_normals_threaded, mesh_obj)
        mesh_obj = future.result()

        texcoords, pil_image_ref, base_color_factor, is_transparent_part = None, None, [0.8, 0.8, 0.8, 1.0], False
        material = None

        if hasattr(mesh_obj, 'visual') and hasattr(mesh_obj.visual, 'material'):
            material = mesh_obj.visual.material
            if hasattr(material, 'baseColorTexture') and isinstance(material.baseColorTexture, Image.Image):
                pil_image_ref = material.baseColorTexture
                img_id = id(pil_image_ref)
                if img_id not in self.pil_images_awaiting_gl_upload:
                    self.pil_images_awaiting_gl_upload[img_id] = pil_image_ref
            if hasattr(material, 'baseColorFactor'):
                bcf = material.baseColorFactor
                if bcf is not None:
                    base_color_factor = [bcf[0], bcf[1], bcf[2], bcf[3] if len(bcf) > 3 else 1.0]

        if hasattr(mesh_obj, 'visual') and hasattr(mesh_obj.visual, 'uv') and len(mesh_obj.visual.uv) == len(mesh_obj.vertices):
            texcoords = np.array(mesh_obj.visual.uv, dtype=np.float32)

        scale, shear, angles, translate, perspective = trimesh.transformations.decompose_matrix(world_transform)

        alpha_mode = getattr(material, 'alphaMode', None) if material else None
        mat_name = (getattr(material, 'name', '') or '').lower() if material else ""

        is_glass_like = ('glass' in mat_name) or (alpha_mode == 'BLEND')
        if is_glass_like:
            base_color_factor[3] = min(base_color_factor[3], 0.35)
            is_transparent_part = True
        else:
            is_transparent_part = base_color_factor[3] < 0.99

        part_data = {
            'name': geom_name_hint,
            'vertices': np.array(mesh_obj.vertices, dtype=np.float32),
            'faces': np.array(mesh_obj.faces, dtype=np.uint32),
            'normals': np.array(mesh_obj.vertex_normals, dtype=np.float32),
            'texcoords': texcoords,
            'position': np.array(translate, dtype=np.float32),
            'rotation': np.array(angles, dtype=np.float32),
            'scale': np.array(scale, dtype=np.float32),
            'pil_image_ref': pil_image_ref,
            'base_color_factor': base_color_factor,
            'vertex_colors': None,
            'is_transparent': is_transparent_part,
            'script_file': None
        }
        self.model_draw_list.append(part_data)

    def load_new_model(self, filepath):
        print(f"\n--- Loading new model: {filepath} ---")
        self.selected_part_index = None
        self.gizmo_handle_meshes.clear()
        self._update_properties_panel()

        # Submit heavy model loading to thread pool
        future = self.thread_pool.submit(self._load_model_threaded, filepath)

        # Show loading indicator
        print("Loading model in background thread...")

        # Process the loaded model when ready
        self.after(100, lambda: self._check_model_loading_complete(future, filepath))

    def _load_model_threaded(self, filepath):
        """Load model file in background thread."""
        try:
            # Use force='mesh' to combine all geometries into a single mesh object.
            # This aligns with the "treat 3D model as a single object" requirement.
            combined_mesh = trimesh.load(filepath, force='mesh', process=True)
            return {'success': True, 'mesh': combined_mesh, 'filepath': filepath}
        except Exception as e:
            return {'success': False, 'error': str(e), 'filepath': filepath}

    def _check_model_loading_complete(self, future, filepath):
        """Check if model loading is complete and process result."""
        if future.done():
            try:
                result = future.result()
                if result['success']:
                    combined_mesh = result['mesh']

                    if isinstance(combined_mesh, trimesh.Trimesh) and not combined_mesh.is_empty:
                        identity_transform = np.eye(4, dtype=np.float32)
                        self._process_mesh_for_drawing(combined_mesh, identity_transform, "imported_model")

                        # Store the original file path in the newly added object
                        if self.model_draw_list:
                            self.model_draw_list[-1]['model_file'] = filepath

                        # Auto-select the newly loaded model
                        self.selected_part_index = len(self.model_draw_list) - 1
                        self._update_gizmo_collision_meshes()
                        self._update_properties_panel()

                        # Update hierarchy list
                        if hasattr(self.app, 'update_hierarchy_list'):
                            self.app.update_hierarchy_list()

                        self.model_loaded = True
                        print(f"--- Model processing complete. Added to scene. Total parts: {len(self.model_draw_list)} ---")
                    else:
                        print("Warning: Loaded model is empty or could not be loaded as a single mesh.")
                else:
                    print(f"FATAL Error loading model: {result['error']}")

                self.event_generate("<Expose>")
            except Exception as e:
                print(f"Error processing loaded model: {e}")
                traceback.print_exc()
        else:
            # Still loading, check again later
            self.after(100, lambda: self._check_model_loading_complete(future, filepath))

    # -------------------------------------------------------------------
    # Duplicate and Delete actions
    # -------------------------------------------------------------------
    def duplicate_selected_part(self):
        """Creates a copy of the currently selected object and adds it to the scene."""
        if self.selected_part_index is None:
            return

        print("Duplicating selected object...")
        original_part = self.model_draw_list[self.selected_part_index]

        # Create a deep copy. This is crucial to ensure the new object is independent.
        new_part = copy.deepcopy(original_part)

        # --- BUG FIX ---
        # The deepcopy also creates a new PIL.Image object. We must point the new part back
        # to the ORIGINAL pil_image_ref so they share the same texture in OpenGL.
        new_part['pil_image_ref'] = original_part['pil_image_ref']

        # Keep the same model_file reference for the duplicated object
        new_part['model_file'] = original_part.get('model_file', None)

        # Offset the new part's position slightly so it's not perfectly overlapping.
        new_part['position'][0] += 1.0

        # Add the new object's data to the master list.
        self.model_draw_list.append(new_part)

        # Select the newly created object.
        self.selected_part_index = len(self.model_draw_list) - 1
        print(f"Object duplicated. New object index: {self.selected_part_index}")

        # Update the gizmo and properties panel to reflect the new selection.
        self._update_gizmo_collision_meshes()
        self._update_properties_panel()

        # Update hierarchy list
        if hasattr(self.app, 'update_hierarchy_list'):
            self.app.update_hierarchy_list()

        self.event_generate("<Expose>")

    def delete_selected_part(self):
        """Removes the currently selected object from the scene."""
        if self.selected_part_index is None:
            return
        
        print(f"Deleting object index: {self.selected_part_index}")
        # Remove the object's data from the master list.
        del self.model_draw_list[self.selected_part_index]
        
        # Clear the selection and gizmo.
        self.selected_part_index = None
        self.gizmo_handle_meshes.clear()
        
        # Update the UI to show that nothing is selected.
        self._update_properties_panel()

        # Update hierarchy list
        if hasattr(self.app, 'update_hierarchy_list'):
            self.app.update_hierarchy_list()

        self.event_generate("<Expose>")
        print("Selected object deleted.")
        
    # -------------------------------------------------------------------
    # UI and Properties Panel Synchronization
    # -------------------------------------------------------------------

    def _update_properties_panel(self):
        """Updates the UI widgets in the side panel with the selected object's data."""
        if self._is_updating_ui: return # Prevent recursive calls
        self._is_updating_ui = True
        
        try:
            if self.selected_part_index is not None and self.selected_part_index < len(self.model_draw_list):
                part = self.model_draw_list[self.selected_part_index]
                
                # --- Update Position Entries ---
                self.app.pos_x_var.set(f"{part['position'][0]:.3f}")
                self.app.pos_y_var.set(f"{part['position'][1]:.3f}")
                self.app.pos_z_var.set(f"{part['position'][2]:.3f}")

                # --- Update Rotation Entries (convert rad to deg for UI) ---
                rot_deg = np.degrees(part['rotation'])
                self.app.rot_x_var.set(f"{rot_deg[0]:.2f}")
                self.app.rot_y_var.set(f"{rot_deg[1]:.2f}")
                self.app.rot_z_var.set(f"{rot_deg[2]:.2f}")

                # --- Update Scale Entries ---
                self.app.scale_x_var.set(f"{part['scale'][0]:.3f}")
                self.app.scale_y_var.set(f"{part['scale'][1]:.3f}")
                self.app.scale_z_var.set(f"{part['scale'][2]:.3f}")

                # --- Update Color Sliders ---
                color = part['base_color_factor']
                self.app.color_r_slider.set(color[0])
                self.app.color_g_slider.set(color[1])
                self.app.color_b_slider.set(color[2])
                # --- ADD THESE TWO LINES ---
                self.app.color_a_slider.set(color[3])
                self.app.color_a_label.configure(text=f"A: {int(color[3]*255)}")

                self.app.color_r_label.configure(text=f"R: {int(color[0]*255)}")
                self.app.color_g_label.configure(text=f"G: {int(color[1]*255)}")
                self.app.color_b_label.configure(text=f"B: {int(color[2]*255)}")



                # --- Update Physics Properties ---
                physics_type = part.get('physics_type', 'None')
                physics_shape = part.get('physics_shape', 'Cube')

                self.app.physics_type_var.set(physics_type)
                self.app.physics_shape_var.set(physics_shape)

                # Validate physics shape options based on object type
                if self.app._is_terrain_object(part):
                    # Terrain objects can only use 2DPlane
                    self.app.physics_shape_menu.configure(values=["2DPlane"])
                    if physics_shape != '2DPlane' and physics_type != 'None':
                        self.app.physics_shape_var.set('2DPlane')
                        part['physics_shape'] = '2DPlane'
                else:
                    # 3D objects can use all shapes except 2DPlane
                    self.app.physics_shape_menu.configure(values=["Cube", "Sphere", "Cylinder", "Cone", "Capsule", "Mesh"])
                    if physics_shape == '2DPlane' and physics_type != 'None':
                        self.app.physics_shape_var.set('Mesh')
                        part['physics_shape'] = 'Mesh'

                # --- Update Mass ---
                mass_value = part.get('mass', 1.0 if physics_type != 'None' else 0.0)
                self.app.mass_var.set(f"{mass_value:.2f}")



                self.app.set_properties_state("normal")
            else:
                # No selection, clear and disable UI
                for var in [self.app.pos_x_var, self.app.pos_y_var, self.app.pos_z_var,
                            self.app.rot_x_var, self.app.rot_y_var, self.app.rot_z_var,
                            self.app.scale_x_var, self.app.scale_y_var, self.app.scale_z_var]:
                    var.set("")
                
                self.app.color_r_slider.set(0)
                self.app.color_g_slider.set(0)
                self.app.color_b_slider.set(0)
                self.app.color_a_slider.set(1)
                self.app.color_r_label.configure(text="R: -")
                self.app.color_g_label.configure(text="G: -")
                self.app.color_b_label.configure(text="B: -")
                self.app.color_a_label.configure(text="A: -")



                # Clear physics properties
                self.app.physics_type_var.set("None")
                self.app.physics_shape_var.set("Cube")
                self.app.mass_var.set("0.0")



                self.app.set_properties_state("disabled")
        finally:
            self._is_updating_ui = False

    def _update_transform_from_ui(self):
        """Reads values from the UI panel and applies them to the selected object."""
        if self._is_updating_ui: return # Prevent feedback loop
        if self.selected_part_index is None: return

        try:
            part = self.model_draw_list[self.selected_part_index]
            
            # --- Position ---
            pos_x = float(self.app.pos_x_var.get())
            pos_y = float(self.app.pos_y_var.get())
            pos_z = float(self.app.pos_z_var.get())
            part['position'] = np.array([pos_x, pos_y, pos_z], dtype=np.float32)

            # --- Rotation (convert deg from UI to rad for calculations) ---
            rot_x = math.radians(float(self.app.rot_x_var.get()))
            rot_y = math.radians(float(self.app.rot_y_var.get()))
            rot_z = math.radians(float(self.app.rot_z_var.get()))
            part['rotation'] = np.array([rot_x, rot_y, rot_z], dtype=np.float32)

            # --- Scale ---
            scale_x = float(self.app.scale_x_var.get())
            scale_y = float(self.app.scale_y_var.get())
            scale_z = float(self.app.scale_z_var.get())
            part['scale'] = np.array([scale_x, scale_y, scale_z], dtype=np.float32)

            # --- Color ---
            r = self.app.color_r_slider.get()
            g = self.app.color_g_slider.get()
            b = self.app.color_b_slider.get()
            # --- ADD THESE THREE LINES ---
            a = self.app.color_a_slider.get()
            part['base_color_factor'] = [r, g, b, a]
            part['is_transparent'] = a < 0.99 # Update transparency status

            # Update color labels
            self.app.color_r_label.configure(text=f"R: {int(r*255)}")
            self.app.color_g_label.configure(text=f"G: {int(g*255)}")
            self.app.color_b_label.configure(text=f"B: {int(b*255)}")
            # --- ADD THIS LINE ---
            self.app.color_a_label.configure(text=f"A: {int(a*255)}")




            # Update gizmo and redraw
            self._update_gizmo_collision_meshes()
            # Rendering will be handled by animate_task automatically

        except (ValueError, TypeError) as e:
            # Handle cases where entry text is not a valid number
            # print(f"Invalid input in properties panel: {e}")
            pass

    # -------------------------------------------------------------------
    # Selection and Gizmo Logic
    # -------------------------------------------------------------------

    def set_gizmo_mode(self, mode):
        self.gizmo_mode = mode
        if self.selected_part_index is not None:
            self._update_gizmo_collision_meshes()
    
    def _screen_to_world_ray(self, x, y):
        y = self.height - y
        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        viewport = glGetIntegerv(GL_VIEWPORT)
        
        near_point = gluUnProject(x, y, 0.0, modelview, projection, viewport)
        far_point = gluUnProject(x, y, 1.0, modelview, projection, viewport)
        
        ray_origin = np.array(near_point, dtype=np.float32)
        ray_direction = np.array(far_point, dtype=np.float32) - ray_origin
        ray_direction /= np.linalg.norm(ray_direction)
        return ray_origin, ray_direction

    def _update_selection(self, ray_origin, ray_direction):
        closest_hit_dist = float('inf')
        new_selected_index = None

        for i, part in enumerate(self.model_draw_list):
            world_transform = self._recompose_transform(part)
            mesh = trimesh.Trimesh(vertices=part['vertices'], faces=part['faces'])
            mesh.apply_transform(world_transform)
            
            intersector = mesh.ray
            locations, index_ray, index_tri = intersector.intersects_location([ray_origin], [ray_direction])
            
            if len(locations) > 0:
                dist = np.linalg.norm(locations[0] - ray_origin)
                if dist < closest_hit_dist:
                    closest_hit_dist = dist
                    new_selected_index = i
        
        selection_changed = self.selected_part_index != new_selected_index
        self.selected_part_index = new_selected_index

        if selection_changed:
            if new_selected_index is not None:
                print(f"Selected model part index: {new_selected_index}")
                self._update_gizmo_collision_meshes()
            else:
                print("Selection cleared.")
                self.gizmo_handle_meshes.clear()
            self._update_properties_panel() # Update UI on any selection change

            # Update hierarchy selection
            if hasattr(self.app, 'update_hierarchy_selection'):
                self.app.update_hierarchy_selection()

    def _get_selected_part_center(self):
        if self.selected_part_index is None: return np.zeros(3)
        part = self.model_draw_list[self.selected_part_index]
        center_local = part['vertices'].mean(axis=0)
        world_transform = self._recompose_transform(part)
        center_world = trimesh.transform_points([center_local], world_transform)[0]
        return center_world

    def _update_gizmo_collision_meshes(self):
        self.gizmo_handle_meshes.clear()
        if self.selected_part_index is None: return

        center = self._get_selected_part_center()
        scale = self._get_gizmo_screen_scale(center)
        
        axis_length = 1.0 * scale
        axis_radius = 0.05 * scale
        arrow_radius = 0.1 * scale
        arrow_height = 0.3 * scale
        ring_radius = 0.8 * scale
        ring_tube_radius = 0.05 * scale

        if self.gizmo_mode == 'translate':
            axes = {'X': [1,0,0], 'Y': [0,1,0], 'Z': [0,0,1]}
            for name, axis in axes.items():
                vec = np.array(axis)
                line_start = center
                line_end = center + vec * axis_length
                cyl = trimesh.creation.cylinder(radius=axis_radius, segment=[line_start, line_end])
                cone_center = center + vec * (axis_length + arrow_height * 0.5)
                cone_transform = trimesh.transformations.rotation_matrix(
                    angle=np.arccos(np.dot([0,0,1], vec)), 
                    direction=np.cross([0,0,1], vec) if np.linalg.norm(np.cross([0,0,1], vec)) > 0 else [1,0,0],
                    point=cone_center
                )
                cone_transform[:3, 3] = cone_center
                cone = trimesh.creation.cone(radius=arrow_radius, height=arrow_height, transform=cone_transform)
                self.gizmo_handle_meshes[name] = trimesh.util.concatenate([cyl, cone])
        
        elif self.gizmo_mode == 'rotate':
            axes = {'X': [1,0,0], 'Y': [0,1,0], 'Z': [0,0,1]}
            for name, axis_vec in axes.items():
                ring = trimesh.creation.torus(major_radius=ring_radius, minor_radius=ring_tube_radius)
                align_transform = trimesh.geometry.align_vectors([0,0,1], axis_vec)
                transform = trimesh.transformations.translation_matrix(center) @ align_transform
                ring.apply_transform(transform)
                self.gizmo_handle_meshes[name] = ring

    def _get_handle_under_mouse(self, ray_origin, ray_direction):
        if not self.gizmo_handle_meshes: return None, float('inf')
        
        closest_hit_dist = float('inf')
        hit_handle = None
        for name, mesh in self.gizmo_handle_meshes.items():
            intersector = mesh.ray
            locations, _, _ = intersector.intersects_location([ray_origin], [ray_direction])
            if len(locations) > 0:
                dist = np.linalg.norm(locations[0] - ray_origin)
                if dist < closest_hit_dist:
                    closest_hit_dist = dist
                    hit_handle = name
        return hit_handle, closest_hit_dist

    def _handle_drag_start(self, x, y, ray_origin, ray_direction):
        print(f"Starting drag on handle: {self.active_gizmo_handle}")
        self.drag_start_mouse = np.array([x, y], dtype=np.float32)
        part = self.model_draw_list[self.selected_part_index]

        # Store initial state for drag calculations
        self.drag_start_position = part['position'].copy()
        self.drag_start_rotation = part['rotation'].copy()
        self.drag_start_scale = part['scale'].copy()
        self.drag_start_transform = self._recompose_transform(part)
        self.drag_start_obj_center = self._get_selected_part_center()

        if self.gizmo_mode == 'translate':
            axis_map = {'X': [1,0,0], 'Y': [0,1,0], 'Z': [0,0,1]}
            axis_vec = np.array(axis_map[self.active_gizmo_handle])
            t = np.cross(axis_vec, self.camera_front)
            self.drag_plane_normal = np.cross(t, axis_vec)
            self.drag_plane_point = self.drag_start_obj_center
        
        elif self.gizmo_mode == 'rotate':
            axis_map = {'X': [1,0,0], 'Y': [0,1,0], 'Z': [0,0,1]}
            self.drag_plane_normal = np.array(axis_map[self.active_gizmo_handle])
            self.drag_plane_point = self.drag_start_obj_center

    def _handle_drag_update(self, x, y):
        if not self.active_gizmo_handle: return

        part = self.model_draw_list[self.selected_part_index]
        ray_origin, ray_direction = self._screen_to_world_ray(x, y)
        
        denom = np.dot(ray_direction, self.drag_plane_normal)
        if abs(denom) < 1e-6: return
        
        t = np.dot(self.drag_plane_point - ray_origin, self.drag_plane_normal) / denom
        if t < 0: return
        
        intersection_point = ray_origin + t * ray_direction

        if self.gizmo_mode == 'translate':
            axis_map = {'X': [1,0,0], 'Y': [0,1,0], 'Z': [0,0,1]}
            axis_vec = np.array(axis_map[self.active_gizmo_handle])
            
            vec_from_center = intersection_point - self.drag_start_obj_center
            projection = np.dot(vec_from_center, axis_vec) * axis_vec
            
            # Update position directly and then update UI
            part['position'] = self.drag_start_position + projection
            self._update_properties_panel()

        elif self.gizmo_mode == 'rotate':
            if not hasattr(self, 'drag_start_vec'):
                self.drag_start_vec = intersection_point - self.drag_start_obj_center
                if np.linalg.norm(self.drag_start_vec) < 1e-6: return
                self.drag_start_vec /= np.linalg.norm(self.drag_start_vec)

            current_vec = intersection_point - self.drag_start_obj_center
            if np.linalg.norm(current_vec) < 1e-6: return
            current_vec /= np.linalg.norm(current_vec)

            angle = math.acos(np.clip(np.dot(self.drag_start_vec, current_vec), -1.0, 1.0))
            cross_prod = np.cross(self.drag_start_vec, current_vec)
            
            if np.dot(self.drag_plane_normal, cross_prod) < 0:
                angle = -angle
            
            T_to_origin = trimesh.transformations.translation_matrix(-self.drag_start_obj_center)
            T_from_origin = trimesh.transformations.translation_matrix(self.drag_start_obj_center)
            R = trimesh.transformations.rotation_matrix(angle, self.drag_plane_normal)
            
            rotation_transform = T_from_origin @ R @ T_to_origin
            new_transform = rotation_transform @ self.drag_start_transform
            
            # Decompose new matrix to get updated T, R, S and apply them
            scale, shear, angles, translate, perspective = trimesh.transformations.decompose_matrix(new_transform)
            part['position'] = translate
            part['rotation'] = angles
            part['scale'] = scale # Rotation can sometimes affect scale slightly
            self._update_properties_panel()

    def _handle_drag_end(self):
        """Cleans up after a drag operation is finished."""
        print(f"Finished drag on handle: {self.active_gizmo_handle}")
        self.active_gizmo_handle = None
        if hasattr(self, 'drag_start_vec'):
            del self.drag_start_vec
        
        if self.selected_part_index is not None:
            self._update_gizmo_collision_meshes()

        # Rendering will be handled by animate_task automatically


    # -------------------------------------------------------------------
    # Rendering
    # -------------------------------------------------------------------

    def _get_gizmo_screen_scale(self, position):
        dist = np.linalg.norm(position - self.camera_pos)
        return dist * 0.1

    def _draw_part(self, part):
        if not (part['vertices'] is not None and part['faces'] is not None and \
                len(part['vertices']) > 0 and len(part['faces']) > 0):
            return

        glPushMatrix()
        world_transform = self._recompose_transform(part)
        glMultMatrixf(world_transform.T.flatten())

        gl_tex_id_to_bind = 0
        if part['pil_image_ref'] is not None:
            pil_img_id_for_part = id(part['pil_image_ref'])
            gl_tex_id_to_bind = self.opengl_texture_map.get(pil_img_id_for_part, 0)
        
        has_texture = gl_tex_id_to_bind != 0 and part['texcoords'] is not None
        has_vcolors = part['vertex_colors'] is not None

        glColor4fv(part['base_color_factor'])
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, part['base_color_factor'])

        if has_texture:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, gl_tex_id_to_bind)
            glEnableClientState(GL_TEXTURE_COORD_ARRAY)
            glTexCoordPointer(2, GL_FLOAT, 0, part['texcoords'])
        else:
            glDisable(GL_TEXTURE_2D)
            if has_vcolors:
                glEnable(GL_COLOR_MATERIAL)
                glEnableClientState(GL_COLOR_ARRAY)
                glColorPointer(4, GL_FLOAT, 0, part['vertex_colors'])

        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, part['vertices'])
        if part['normals'] is not None:
            glEnableClientState(GL_NORMAL_ARRAY)
            glNormalPointer(GL_FLOAT, 0, part['normals'])

        glDrawElements(GL_TRIANGLES, part['faces'].size, GL_UNSIGNED_INT, part['faces'].flatten())

        glDisableClientState(GL_VERTEX_ARRAY)
        if part['normals'] is not None: glDisableClientState(GL_NORMAL_ARRAY)
        if has_texture:
            glDisableClientState(GL_TEXTURE_COORD_ARRAY)
            glBindTexture(GL_TEXTURE_2D, 0)
            glDisable(GL_TEXTURE_2D)
        if has_vcolors:
            glDisableClientState(GL_COLOR_ARRAY)
            glDisable(GL_COLOR_MATERIAL)
        glPopMatrix()


    def _draw_world_origin_gizmo(self):
        if not self.show_world_gizmo: return
        glPushAttrib(GL_ENABLE_BIT | GL_LINE_BIT | GL_CURRENT_BIT)
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        glLineWidth(2.5)
        glBegin(GL_LINES)
        glColor3f(1.0, 0.0, 0.0); glVertex3f(0,0,0); glVertex3f(self.gizmo_length, 0, 0)
        glColor3f(0.0, 1.0, 0.0); glVertex3f(0,0,0); glVertex3f(0, self.gizmo_length, 0)
        glColor3f(0.0, 0.0, 1.0); glVertex3f(0,0,0); glVertex3f(0, 0, self.gizmo_length)
        glEnd()
        glPopAttrib()

    def _draw_sun(self):
        """Draws a realistic 3D sun in the sky."""
        # Check if sun is visible
        if not getattr(self.app, 'sun_visible', True):
            return

        glPushAttrib(GL_ALL_ATTRIB_BITS)
        glEnable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Sun position (high in the sky, slightly to the right)
        sun_pos = np.array([50.0, 40.0, -30.0])

        # Draw realistic 3D sun sphere
        glPushMatrix()
        glTranslatef(sun_pos[0], sun_pos[1], sun_pos[2])

        # Create quadric for sphere
        quad = gluNewQuadric()
        gluQuadricNormals(quad, GLU_SMOOTH)
        gluQuadricTexture(quad, GL_TRUE)

        # Sun material - use dynamic color from app
        sun_material = self.app.sun_color
        glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, sun_material)
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, sun_material)
        glColor4f(sun_material[0], sun_material[1], sun_material[2], sun_material[3])

        # Draw 3D sun sphere
        sun_radius = 2.0
        gluSphere(quad, sun_radius, 32, 16)

        # Reset emission
        glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])

        # Draw 3D atmospheric glow halo
        glDisable(GL_LIGHTING)
        glDepthMask(GL_FALSE)

        # Create 3D halo sphere
        halo_quad = gluNewQuadric()
        gluQuadricNormals(halo_quad, GLU_SMOOTH)

        # Use dynamic halo color from app
        glow_color = self.app.halo_color
        glColor4f(glow_color[0], glow_color[1], glow_color[2], glow_color[3])

        # Draw 3D halo sphere
        halo_radius = sun_radius * 2.5
        gluSphere(halo_quad, halo_radius, 24, 12)

        gluDeleteQuadric(halo_quad)
        glDepthMask(GL_TRUE)
        gluDeleteQuadric(quad)
        glPopMatrix()
        glPopAttrib()

    def _apply_hbao_lighting(self):
        """Apply HBAO-style lighting for ambient occlusion effect."""
        # Update light positions based on camera for horizon-based effect
        cam_right = self.camera_right
        cam_up = self.camera_up
        cam_front = self.camera_front

        # Position lights around the horizon relative to camera
        glLightfv(GL_LIGHT1, GL_POSITION, [cam_up[0], cam_up[1], cam_up[2], 0.0])
        glLightfv(GL_LIGHT2, GL_POSITION, [cam_right[0], cam_right[1], cam_right[2], 0.0])
        glLightfv(GL_LIGHT3, GL_POSITION, [-cam_right[0], -cam_right[1], -cam_right[2], 0.0])

    def _draw_part_with_hbao(self, part, sun_direction_world, view_pos):
        """Draw part with high-quality rendering, HBAO effect, and dedicated terrain shader path."""
        if not (part.get('vertices') is not None and part.get('faces') is not None and \
                len(part['vertices']) > 0 and len(part['faces']) > 0):
            return

        is_terrain = part.get('is_terrain', False)

        if is_terrain and self.terrain_shader:
            # --- TERRAIN SHADER RENDER PATH ---
            if part.get('VAO') is None:
                self._setup_terrain_buffers(part)
                if part.get('VAO') is None: return

            glUseProgram(self.terrain_shader)

            # Cache uniform locations for performance
            if not hasattr(self, '_terrain_shader_locs'):
                self._terrain_shader_locs = {
                    'model': glGetUniformLocation(self.terrain_shader, "model"),
                    'view': glGetUniformLocation(self.terrain_shader, "view"),
                    'projection': glGetUniformLocation(self.terrain_shader, "projection"),
                    'sunDirection': glGetUniformLocation(self.terrain_shader, "sunDirection_World"),
                    'viewPos': glGetUniformLocation(self.terrain_shader, "viewPos"),
                    'tex0': glGetUniformLocation(self.terrain_shader, "texture_slot0"),
                    'tex1': glGetUniformLocation(self.terrain_shader, "texture_slot1"),
                    'tex2': glGetUniformLocation(self.terrain_shader, "texture_slot2"),
                    'has_tex0': glGetUniformLocation(self.terrain_shader, "has_texture_slot0"),
                    'has_tex1': glGetUniformLocation(self.terrain_shader, "has_texture_slot1"),
                    'has_tex2': glGetUniformLocation(self.terrain_shader, "has_texture_slot2"),
                    'color0': glGetUniformLocation(self.terrain_shader, "color_slot0"),
                    'color1': glGetUniformLocation(self.terrain_shader, "color_slot1"),
                    'color2': glGetUniformLocation(self.terrain_shader, "color_slot2"),
                    # --- NEW UNIFORM LOCATIONS ---
                    'sunColor': glGetUniformLocation(self.terrain_shader, "sunColor"),
                    'horizonColor': glGetUniformLocation(self.terrain_shader, "horizonColor"),
                    'fogDensity': glGetUniformLocation(self.terrain_shader, "fogDensity"),
                    'fogGradient': glGetUniformLocation(self.terrain_shader, "fogGradient"),
                }
            locs = self._terrain_shader_locs

            world_transform = self._recompose_transform(part)
            # --- FIX 1: Transpose the row-major world_transform matrix for OpenGL ---
            glUniformMatrix4fv(locs['model'], 1, GL_FALSE, world_transform.T)
            glUniformMatrix4fv(locs['view'], 1, GL_FALSE, glGetFloatv(GL_MODELVIEW_MATRIX))
            glUniformMatrix4fv(locs['projection'], 1, GL_FALSE, glGetFloatv(GL_PROJECTION_MATRIX))
            glUniform3fv(locs['sunDirection'], 1, sun_direction_world)
            glUniform3fv(locs['viewPos'], 1, view_pos)

            # --- PASS NEW ENVIRONMENT UNIFORMS ---
            # Get sun elevation to calculate sunset color mix
            sun_elevation = sun_direction_world[1]
            sunset_factor = np.clip((0.25 - sun_elevation) / 0.25, 0.0, 1.0)

            # Calculate dynamic sun color (matches sunset in sky shader)
            sunset_color = np.array([0.9, 0.5, 0.2])
            base_sun_color = np.array(self.app.sun_color[:3])
            dynamic_sun_color = base_sun_color * (1.0 - sunset_factor) + (sunset_color * 1.5) * sunset_factor
            glUniform3fv(locs['sunColor'], 1, dynamic_sun_color)

            # Pass horizon color for ambient light and fog
            glUniform3fv(locs['horizonColor'], 1, self.app.horizon_color_val)

            # Pass fog settings from the UI
            glUniform1f(locs['fogDensity'], self.app.fog_density)
            glUniform1f(locs['fogGradient'], self.app.fog_gradient)
            # --- END OF NEW UNIFORMS ---

            props = part.get('terrain_properties', {})
            slot_colors = props.get('slot_colors', [[1,1,1,1]]*3)

            for i in range(3):
                glUniform4fv(locs[f'color{i}'], 1, slot_colors[i])

                tex_id = self.terrain_textures.get(i)
                if tex_id:
                    glActiveTexture(GL_TEXTURE0 + i)
                    glBindTexture(GL_TEXTURE_2D, tex_id)
                    glUniform1i(locs[f'tex{i}'], i)
                    glUniform1i(locs[f'has_tex{i}'], 1)
                else:
                    glUniform1i(locs[f'has_tex{i}'], 0)

            glBindVertexArray(part['VAO'])
            glDrawElements(GL_TRIANGLES, part['faces'].size, GL_UNSIGNED_INT, None)

            glBindVertexArray(0)
            glUseProgram(0)
            glActiveTexture(GL_TEXTURE0)

        else:
            # --- NEW: GENERIC MESH SHADER PATH ---
            if part.get('VAO') is None:          # safety
                self._setup_mesh_buffers(part)

            glUseProgram(self.generic_mesh_shader)   # we create this below
            loc = self._generic_mesh_locs            # cached uniforms

            world = part.get('world_transform', self._recompose_transform(part))
            # --- FIX 2: Transpose the row-major world matrix for OpenGL ---
            glUniformMatrix4fv(loc['model'], 1, GL_FALSE, world.T)
            glUniformMatrix4fv(loc['view'],  1, GL_FALSE, glGetFloatv(GL_MODELVIEW_MATRIX))
            glUniformMatrix4fv(loc['proj'], 1, GL_FALSE, glGetFloatv(GL_PROJECTION_MATRIX))

            # lighting & colour
            glUniform3fv(loc['sunDir'],  1, sun_direction_world)
            glUniform3fv(loc['sunCol'],  1, self.app.sun_color[:3])
            glUniform3fv(loc['horizon'], 1, self.app.horizon_color_val)
            glUniform3fv(loc['viewPos'], 1, view_pos)
            glUniform4fv(loc['baseCol'], 1, part['base_color_factor'])

            # texture
            tex_id = self.opengl_texture_map.get(id(part.get('pil_image_ref')), 0)
            glUniform1i(loc['hasTex'], 1 if tex_id else 0)
            if tex_id:
                glActiveTexture(GL_TEXTURE0)
                glBindTexture(GL_TEXTURE_2D, tex_id)
                glUniform1i(loc['tex'], 0)

            # draw
            glBindVertexArray(part['VAO'])
            glDrawElements(GL_TRIANGLES, part['faces'].size, GL_UNSIGNED_INT, None)
            glBindVertexArray(0)
            glUseProgram(0)

    def _draw_selection_gizmo(self):
        if self.selected_part_index is None: return

        center = self._get_selected_part_center()
        scale = self._get_gizmo_screen_scale(center)

        glPushAttrib(GL_ALL_ATTRIB_BITS)
        glEnable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        glPushMatrix()
        glTranslatef(center[0], center[1], center[2])
        glScalef(scale, scale, scale)

        if self.gizmo_mode == 'translate':
            self._draw_translate_handle('X', np.array([1.0, 0.0, 0.0]))
            self._draw_translate_handle('Y', np.array([0.0, 1.0, 0.0]))
            self._draw_translate_handle('Z', np.array([0.0, 0.0, 1.0]))
        elif self.gizmo_mode == 'rotate':
            self._draw_rotate_handle('X', np.array([1.0, 0.0, 0.0]))
            self._draw_rotate_handle('Y', np.array([0.0, 1.0, 0.0]))
            self._draw_rotate_handle('Z', np.array([0.0, 0.0, 1.0]))

        glPopMatrix()
        glPopAttrib()

    def _draw_translate_handle(self, name, axis_vec):
        color = np.abs(axis_vec)
        highlight_color = [1.0, 1.0, 0.0, 1.0]
        base_material = [color[0], color[1], color[2], 1.0]
        
        if name == self.active_gizmo_handle:
            glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, highlight_color)
            glColor4f(*highlight_color)  # Explicit color for visibility
        else:
            glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, base_material)
            glColor4f(*base_material)  # Explicit color for visibility

        quad = gluNewQuadric()
        
        z_axis = np.array([0.0, 0.0, 1.0])
        angle = math.acos(np.dot(z_axis, axis_vec))
        rot_axis = np.cross(z_axis, axis_vec)
        if np.linalg.norm(rot_axis) < 1e-6:
            rot_axis = np.array([1.0, 0.0, 0.0])

        glPushMatrix()
        glRotatef(math.degrees(angle), rot_axis[0], rot_axis[1], rot_axis[2])
        
        shaft_radius = 0.05
        shaft_length = 0.75
        gluCylinder(quad, shaft_radius, shaft_radius, shaft_length, 12, 1)

        cone_radius = 0.12
        cone_height = 0.25
        glTranslatef(0, 0, shaft_length)
        gluCylinder(quad, cone_radius, 0.0, cone_height, 12, 1)
        
        glPopMatrix()
        gluDeleteQuadric(quad)

    def _draw_rotate_handle(self, name, axis_vec):
        color = np.abs(axis_vec)
        highlight_color = [1.0, 1.0, 0.0, 1.0]
        base_material = [color[0], color[1], color[2], 1.0]

        if name == self.active_gizmo_handle:
            glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, highlight_color)
            glColor4f(*highlight_color)  # Explicit color for visibility
        else:
            glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, base_material)
            glColor4f(*base_material)  # Explicit color for visibility
        
        glPushMatrix()
        
        z_axis = np.array([0.0, 0.0, 1.0])
        angle = math.acos(np.dot(z_axis, axis_vec))
        rot_axis = np.cross(z_axis, axis_vec)
        if np.linalg.norm(rot_axis) < 1e-6:
             rot_axis = np.array([1.0, 0.0, 0.0])

        glRotatef(math.degrees(angle), rot_axis[0], rot_axis[1], rot_axis[2])
        self._draw_solid_torus(0.8, 0.05, 32, 16)
        glPopMatrix()

    def _draw_solid_torus(self, major_radius, minor_radius, num_major, num_minor):
        for i in range(num_major):
            glBegin(GL_QUAD_STRIP)
            for j in range(num_minor + 1):
                for k in [0, 1]:
                    major_angle = 2.0 * math.pi * (i + k) / num_major
                    minor_angle = 2.0 * math.pi * j / num_minor
                    x = (major_radius + minor_radius * math.cos(minor_angle)) * math.cos(major_angle)
                    y = (major_radius + minor_radius * math.cos(minor_angle)) * math.sin(major_angle)
                    z = minor_radius * math.sin(minor_angle)
                    normal_center_x = major_radius * math.cos(major_angle)
                    normal_center_y = major_radius * math.sin(major_angle)
                    normal_x = x - normal_center_x
                    normal_y = y - normal_center_y
                    normal_z = z
                    norm = np.linalg.norm([normal_x, normal_y, normal_z])
                    if norm > 1e-6:
                        normal_x /= norm; normal_y /= norm; normal_z /= norm
                    glNormal3f(normal_x, normal_y, normal_z)
                    glVertex3f(x, y, z)
            glEnd()

    def _update_brush_position(self):
        """Update brush visualizer position based on mouse cursor and terrain intersection."""
        if not self.brush_visualizer:
            return

        # Get current mouse position (use last known position)
        mouse_x = getattr(self, 'last_mouse_x', self.width // 2)
        mouse_y = getattr(self, 'last_mouse_y', self.height // 2)

        # Calculate ray from mouse position
        ray_origin, ray_direction = self._screen_to_world_ray(mouse_x, mouse_y)

        # Find intersection with terrain
        brush_display_position = None
        can_interact_here = False

        if self.current_terrain_obj:
            terrain_hit_point = ray_terrain_intersection(ray_origin, ray_direction, self.current_terrain_obj)

            if terrain_hit_point is not None:
                # Position brush slightly above terrain surface
                brush_display_position = terrain_hit_point + np.array([0, 0.05, 0], dtype=np.float32)
                can_interact_here = True
            else:
                # Position brush at fixed distance if no terrain hit
                brush_display_position = ray_origin + ray_direction * 100.0
                can_interact_here = False

            # Update brush transform with current size
            self.brush_visualizer.update_transform(brush_display_position, self.terrain_brush_size)

            # Set brush visibility based on interaction capability
            self.brush_visualizer.visible = True
        else:
            self.brush_visualizer.visible = False

    def _draw_brush_visualizer(self, view_matrix, projection_matrix):
        """Draw the brush visualizer circle."""
        if not self.brush_visualizer or not self.brush_visualizer.visible:
            return

        # Disable depth testing for brush overlay
        glDisable(GL_DEPTH_TEST)

        # Draw the brush circle
        self.brush_visualizer.draw(view_matrix, projection_matrix)

        # Re-enable depth testing
        glEnable(GL_DEPTH_TEST)

    def redraw(self):
        self._create_and_cache_missing_gl_textures()

        # Update time for cloud animation
        self.current_time_gl = time.time() - self.start_time

        # If FXAA is enabled, render to framebuffer first
        if self.fxaa_enabled and self.fxaa_fbo:
            self._render_with_fxaa()
        else:
            self._render_scene()

    def _render_scene(self):
        """Render the main scene."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Update fog color every frame
        fog_color = self.app.sky_color
        glFogfv(GL_FOG_COLOR, fog_color)

        # Setup projection matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect_ratio = self.width / self.height if self.height > 0 else 1.0
        gluPerspective(45, aspect_ratio, 0.5, 5000.0)
        projection_matrix_gl = glGetFloatv(GL_PROJECTION_MATRIX)

        # Setup view matrix
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        look_at_point = self.camera_pos + self.camera_front
        gluLookAt(self.camera_pos[0], self.camera_pos[1], self.camera_pos[2],
                  look_at_point[0], look_at_point[1], look_at_point[2],
                  self.camera_up[0], self.camera_up[1], self.camera_up[2])
        view_matrix_gl = glGetFloatv(GL_MODELVIEW_MATRIX)

        sun_direction_world = np.array([0.8, 0.7, -0.6], dtype=np.float32)
        norm = np.linalg.norm(sun_direction_world)
        if norm > 1e-6:
            sun_direction_world /= norm

        # Render sky with clouds if sky renderer is available
        if self.sky_renderer is not None:
            try:
                inv_projection_matrix = np.linalg.inv(projection_matrix_gl)
                inv_view_matrix = np.linalg.inv(view_matrix_gl)

                # Render sky behind everything
                glDepthMask(GL_FALSE)

                sky_base = self.app.sky_color[:3]
                zenith_color = [c * 0.8 for c in sky_base]
                horizon_color = [min(1.0, c * 1.2) for c in sky_base]
                self.app.horizon_color_val = horizon_color

                self.sky_renderer.draw(
                    inv_projection_matrix,
                    inv_view_matrix,
                    self.current_time_gl,
                    sun_direction_world,
                    zenith_color,
                    horizon_color
                )
                glDepthMask(GL_TRUE)
            except np.linalg.LinAlgError:
                print("ERROR: Could not invert projection/view matrix for sky rendering.")

        self._draw_world_origin_gizmo()
        self._draw_sun()

        if self.model_loaded and self.model_draw_list:
            glEnable(GL_LIGHTING)
            self._apply_hbao_lighting()

            opaque_parts = [p for p in self.model_draw_list if not p.get('is_transparent', False)]
            transparent_parts = [p for p in self.model_draw_list if p.get('is_transparent', False)]

            glDisable(GL_BLEND)
            glDepthMask(GL_TRUE)
            for part in opaque_parts:
                self._draw_part_with_hbao(part, sun_direction_world, self.camera_pos)

            if transparent_parts:
                glEnable(GL_BLEND)
                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                glDepthMask(GL_FALSE)
                for part in transparent_parts:
                    self._draw_part_with_hbao(part, sun_direction_world, self.camera_pos)
                glDepthMask(GL_TRUE)
                glDisable(GL_BLEND)

        if self.fps_mouse_sensitivity is None:
            self._draw_selection_gizmo()

        if (self.terrain_editing_mode and self.current_terrain_obj and
            self.brush_visualizer and self.brush_shader):
            self._update_brush_position()
            self._draw_brush_visualizer(view_matrix_gl, projection_matrix_gl)

    def _render_with_fxaa(self):
        """Render scene with FXAA anti-aliasing."""
        # First pass: Render scene to framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, self.fxaa_fbo)
        glViewport(0, 0, self.screen_width, self.screen_height)

        # Render the scene normally
        self._render_scene()

        # Second pass: Apply FXAA and render to screen
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glViewport(0, 0, self.width, self.height)
        glClear(GL_COLOR_BUFFER_BIT)

        # Disable depth testing for screen quad
        glDisable(GL_DEPTH_TEST)

        # Use FXAA shader
        glUseProgram(self.fxaa_shader_program)

        # Bind the rendered texture
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.fxaa_color_texture)
        glUniform1i(glGetUniformLocation(self.fxaa_shader_program, "screenTexture"), 0)

        # Set screen size uniform
        glUniform2f(glGetUniformLocation(self.fxaa_shader_program, "screenSize"),
                   float(self.screen_width), float(self.screen_height))

        # Render screen quad
        glBindVertexArray(self.fxaa_vao)
        glDrawArrays(GL_TRIANGLES, 0, 6)
        glBindVertexArray(0)

        # Re-enable depth testing
        glEnable(GL_DEPTH_TEST)

        glUseProgram(0)

    def animate_task(self):
        self._update_camera_position()
        self.event_generate("<Expose>")
        self._after_id = self.after(16, self.animate_task)

    def cleanup_gl_resources(self):
        print("Cleaning up GL resources...")
        self._cleanup_old_model_resources()

        # Cleanup FXAA resources
        try:
            if self.fxaa_fbo:
                glDeleteFramebuffers(1, [self.fxaa_fbo])
            if self.fxaa_color_texture:
                glDeleteTextures(1, [self.fxaa_color_texture])
            if self.fxaa_depth_texture:
                glDeleteTextures(1, [self.fxaa_depth_texture])
            if self.fxaa_vao:
                glDeleteVertexArrays(1, [self.fxaa_vao])
            if self.fxaa_vbo:
                glDeleteBuffers(1, [self.fxaa_vbo])
            if self.fxaa_shader_program:
                glDeleteProgram(self.fxaa_shader_program)
            print("FXAA resources cleaned up")
        except Exception as e:
            print(f"Error cleaning up FXAA resources: {e}")

        # Cleanup threading resources
        try:
            print("Shutting down thread pool...")
            self.thread_pool.shutdown(wait=True)
            print("Thread pool shutdown complete.")
        except Exception as e:
            print(f"Error shutting down thread pool: {e}")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Hamid PY Engine V1.4")
        self.geometry("1235x850")

        # Initialize sun visibility BEFORE UI creation
        self.sun_visible = True

        # --- Main Layout ---
        self.grid_columnconfigure(1, weight=1)  # Middle column (OpenGL) gets the weight
        self.grid_rowconfigure(2, weight=1)  # Changed to accommodate menu bar

        # --- Unity-like Menu Bar ---
        self.create_menu_bar()

        # --- Top control frame ---
        top_frame = ctk.CTkFrame(self)
        top_frame.grid(row=1, column=0, columnspan=3, pady=5, padx=10, sticky="ew")

        self.load_button = ctk.CTkButton(top_frame, text="Load .glb/.gltf Model", command=self.open_file_dialog)
        self.load_button.pack(side="left", padx=5)

        gizmo_label = ctk.CTkLabel(top_frame, text="Gizmo Mode:")
        gizmo_label.pack(side="left", padx=(20, 5))
        self.translate_button = ctk.CTkButton(top_frame, text="Translate (T)", command=lambda: self.set_gizmo_mode('translate'))
        self.translate_button.pack(side="left", padx=5)
        self.rotate_button = ctk.CTkButton(top_frame, text="Rotate (R)", command=lambda: self.set_gizmo_mode('rotate'))
        self.rotate_button.pack(side="left", padx=5)

        # Fog and Sky Color buttons
        self.sky_color_button = ctk.CTkButton(top_frame, text="Sky Color", command=self.choose_sky_color, width=80)
        self.sky_color_button.pack(side="left", padx=(20, 5))

        self.halo_color_button = ctk.CTkButton(top_frame, text="Halo Color", command=self.choose_halo_color, width=80)
        self.halo_color_button.pack(side="left", padx=5)

        self.sun_color_button = ctk.CTkButton(top_frame, text="Sun Color", command=self.choose_sun_color, width=80)
        self.sun_color_button.pack(side="left", padx=5)

        # Sun visibility checkbox (use initialized sun_visible state)
        self.sun_visible_var = ctk.BooleanVar(value=self.sun_visible)
        self.sun_visible_checkbox = ctk.CTkCheckBox(
            top_frame,
            text="Show Sun",
            variable=self.sun_visible_var,
            command=self.toggle_sun_visibility,
            width=80
        )
        self.sun_visible_checkbox.pack(side="left", padx=5)

        # Terrain Editor button
        self.terrain_button = ctk.CTkButton(top_frame, text="Terrain Editor", command=self.open_terrain_editor, width=100)
        self.terrain_button.pack(side="left", padx=(20, 5))

        # Play button
        self.play_button = ctk.CTkButton(top_frame, text="Play", command=self.toggle_physics, width=60)
        self.play_button.pack(side="left", padx=(20, 5))

        # --- Left Panel (Hierarchy) ---
        self.hierarchy_frame = ctk.CTkScrollableFrame(self, label_text="Hierarchy", width=200)
        self.hierarchy_frame.grid(row=2, column=0, sticky="ns", padx=(10,5), pady=(0,10))

        # --- OpenGL Frame ---
        self.gl_frame = CubeOpenGLFrame(self, app=self, width=800, height=600)
        self.gl_frame.grid(row=2, column=1, sticky="nsew", padx=5, pady=(0,10))

        # --- Properties Panel ---
        self.properties_frame = ctk.CTkScrollableFrame(self, label_text="Properties", width=235)
        self.properties_frame.grid(row=2, column=2, sticky="ns", padx=(5,10), pady=(0,10))

        # --- Console Panel ---
        self.console_frame = ctk.CTkFrame(self, height=50)
        self.console_frame.grid(row=3, column=0, columnspan=3, sticky="ew", padx=10, pady=(0,10))
        self.console_frame.grid_columnconfigure(0, weight=1)

        console_label = ctk.CTkLabel(self.console_frame, text="Console", font=ctk.CTkFont(size=12, weight="bold"))
        console_label.grid(row=0, column=0, sticky="w", padx=10, pady=2)

        self.console_text = ctk.CTkTextbox(self.console_frame, height=50, font=ctk.CTkFont(family="Consolas", size=10))
        self.console_text.grid(row=1, column=0, sticky="ew", padx=10, pady=(0,10))

        self.create_properties_widgets()
        self.create_hierarchy_widgets()

        # Redirect print statements to console
        self._setup_console_redirect()

        # Initialize button states based on sun visibility
        self.after(100, self._initialize_sun_button_states)

        # Initialize default colors (from TheHigh V1)
        self.sun_color = [1.0, 0.9, 0.7, 1.0]  # Warm sun color
        self.sky_color = [0.6, 0.7, 0.9, 1.0]  # Beautiful sky color from TheHigh V1
        self.halo_color = [1.0, 0.9, 0.7, 0.15]  # Default halo color

        # ADD THESE THREE LINES:
        self.horizon_color_val = [0.6, 0.7, 0.9] # For terrain shader
        self.fog_density = 0.003
        self.fog_gradient = 1.5

        # Physics system
        self.physics_enabled = False
        self.physics_objects = []
        self.last_physics_time = 0
        self.scene_backup = None

        # FPS Controller system
        self.fps_mode = False
        self.fps_camera_backup = None

        self.after(100, self.gl_frame.animate_task)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.bind('t', lambda e: self.set_gizmo_mode('translate'))
        self.bind('r', lambda e: self.set_gizmo_mode('rotate'))
        self.after(100, lambda: self.gl_frame.focus_set())
        
        self.gl_frame._update_properties_panel() # Initial UI state

    def _setup_console_redirect(self):
        """Setup console to capture print statements."""
        import sys

        class ConsoleRedirect:
            def __init__(self, console_widget):
                self.console_widget = console_widget
                self.original_stdout = sys.stdout

            def write(self, text):
                try:
                    if text.strip() and self.console_widget:  # Only show non-empty messages
                        # Schedule GUI update in main thread
                        self.console_widget.after(0, self._update_console, text.strip())
                except Exception as e:
                    # Fallback to original stdout if console fails
                    pass
                # Also write to original stdout for debugging
                if self.original_stdout:
                    self.original_stdout.write(text)

            def flush(self):
                try:
                    if self.original_stdout:
                        self.original_stdout.flush()
                except Exception:
                    pass

            def _update_console(self, text):
                try:
                    if self.console_widget and hasattr(self.console_widget, 'insert'):
                        # Insert text at end
                        self.console_widget.insert("end", text + "\n")
                        # Auto-scroll to bottom
                        self.console_widget.see("end")
                        # Limit console to last 100 lines
                        lines = self.console_widget.get("1.0", "end").split('\n')
                        if len(lines) > 100:
                            self.console_widget.delete("1.0", f"{len(lines)-100}.0")
                except Exception as e:
                    # Silently fail if console is not available
                    pass

        # Redirect stdout to console
        try:
            if hasattr(self, 'console_text') and self.console_text:
                sys.stdout = ConsoleRedirect(self.console_text)
                # Add welcome message
                print("FreeFly Game Engine Console - Ready")
            else:
                print("Warning: Console widget not available, using standard output")
        except Exception as e:
            print(f"Warning: Could not setup console redirect: {e}")

    def create_menu_bar(self):
        """Creates a Unity-like menu bar with File, Edit, View, and Help menus."""
        menu_frame = ctk.CTkFrame(self, height=35)
        menu_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        menu_frame.grid_propagate(False)

        # File Menu
        file_menu_button = ctk.CTkButton(
            menu_frame, text="File", width=60, height=30,
            command=self.show_file_menu, corner_radius=0
        )
        file_menu_button.pack(side="left", padx=2, pady=2)

        # Edit Menu
        edit_menu_button = ctk.CTkButton(
            menu_frame, text="Edit", width=60, height=30,
            command=self.show_edit_menu, corner_radius=0
        )
        edit_menu_button.pack(side="left", padx=2, pady=2)

        # View Menu
        view_menu_button = ctk.CTkButton(
            menu_frame, text="View", width=60, height=30,
            command=self.show_view_menu, corner_radius=0
        )
        view_menu_button.pack(side="left", padx=2, pady=2)

        # GameObject Menu
        gameobject_menu_button = ctk.CTkButton(
            menu_frame, text="GameObject", width=80, height=30,
            command=self.show_gameobject_menu, corner_radius=0
        )
        gameobject_menu_button.pack(side="left", padx=2, pady=2)

        # Window Menu
        window_menu_button = ctk.CTkButton(
            menu_frame, text="Window", width=70, height=30,
            command=self.show_window_menu, corner_radius=0
        )
        window_menu_button.pack(side="left", padx=2, pady=2)

        # Help Menu
        help_menu_button = ctk.CTkButton(
            menu_frame, text="Help", width=60, height=30,
            command=self.show_help_menu, corner_radius=0
        )
        help_menu_button.pack(side="left", padx=2, pady=2)

    def show_file_menu(self):
        """Shows the File menu with save/load options."""
        file_menu = ctk.CTkToplevel(self)
        file_menu.title("File")
        file_menu.geometry("200x150")
        file_menu.resizable(False, False)

        # Position menu near the File button
        file_menu.geometry("+100+50")

        # Bring window to front
        file_menu.transient(self)
        file_menu.lift()
        file_menu.focus_set()
        file_menu.attributes("-topmost", True)
        file_menu.after(100, lambda: file_menu.attributes("-topmost", False))

        # New Scene
        new_button = ctk.CTkButton(file_menu, text="New Scene", command=self.new_scene)
        new_button.pack(pady=5, padx=10, fill="x")

        # Save Scene
        save_button = ctk.CTkButton(file_menu, text="Save Scene", command=self.save_scene)
        save_button.pack(pady=5, padx=10, fill="x")

        # Load Scene
        load_button = ctk.CTkButton(file_menu, text="Load Scene", command=self.load_scene)
        load_button.pack(pady=5, padx=10, fill="x")

        # Load Model
        load_model_button = ctk.CTkButton(file_menu, text="Load Model", command=self.open_file_dialog)
        load_model_button.pack(pady=5, padx=10, fill="x")

    def show_edit_menu(self):
        """Shows the Edit menu with object manipulation options."""
        edit_menu = ctk.CTkToplevel(self)
        edit_menu.title("Edit")
        edit_menu.geometry("200x120")
        edit_menu.resizable(False, False)
        edit_menu.geometry("+170+50")

        # Bring window to front
        edit_menu.transient(self)
        edit_menu.lift()
        edit_menu.focus_set()
        edit_menu.attributes("-topmost", True)
        edit_menu.after(100, lambda: edit_menu.attributes("-topmost", False))

        # Duplicate
        duplicate_button = ctk.CTkButton(edit_menu, text="Duplicate", command=self.duplicate_selected_object)
        duplicate_button.pack(pady=5, padx=10, fill="x")

        # Delete
        delete_button = ctk.CTkButton(edit_menu, text="Delete", command=self.delete_selected_object)
        delete_button.pack(pady=5, padx=10, fill="x")

    def show_view_menu(self):
        """Shows the View menu with display options."""
        view_menu = ctk.CTkToplevel(self)
        view_menu.title("View")
        view_menu.geometry("200x120")
        view_menu.resizable(False, False)
        view_menu.geometry("+240+50")

        # Bring window to front
        view_menu.transient(self)
        view_menu.lift()
        view_menu.focus_set()
        view_menu.attributes("-topmost", True)
        view_menu.after(100, lambda: view_menu.attributes("-topmost", False))

        # Toggle World Gizmo
        gizmo_button = ctk.CTkButton(
            view_menu, text="Toggle World Gizmo",
            command=lambda: setattr(self.gl_frame, 'show_world_gizmo', not self.gl_frame.show_world_gizmo)
        )
        gizmo_button.pack(pady=5, padx=10, fill="x")

    def show_gameobject_menu(self):
        """Shows the GameObject menu with 3D primitive options."""
        gameobject_menu = ctk.CTkToplevel(self)
        gameobject_menu.title("GameObject")
        gameobject_menu.geometry("200x225")
        gameobject_menu.resizable(False, False)
        gameobject_menu.geometry("+380+50")

        # Bring window to front
        gameobject_menu.transient(self)
        gameobject_menu.lift()
        gameobject_menu.focus_set()
        gameobject_menu.attributes("-topmost", True)
        gameobject_menu.after(100, lambda: gameobject_menu.attributes("-topmost", False))

        # Cube
        cube_button = ctk.CTkButton(gameobject_menu, text="Cube", command=self.create_cube)
        cube_button.pack(pady=5, padx=10, fill="x")

        # Sphere
        sphere_button = ctk.CTkButton(gameobject_menu, text="Sphere", command=self.create_sphere)
        sphere_button.pack(pady=5, padx=10, fill="x")

        # Cone
        cone_button = ctk.CTkButton(gameobject_menu, text="Cone", command=self.create_cone)
        cone_button.pack(pady=5, padx=10, fill="x")

        # Cylinder
        cylinder_button = ctk.CTkButton(gameobject_menu, text="Cylinder", command=self.create_cylinder)
        cylinder_button.pack(pady=5, padx=10, fill="x")

        # Capsule
        capsule_button = ctk.CTkButton(gameobject_menu, text="Capsule", command=self.create_capsule)
        capsule_button.pack(pady=5, padx=10, fill="x")

        # Enemy
        enemy_button = ctk.CTkButton(gameobject_menu, text="Enemy", command=self.create_enemy)
        enemy_button.pack(pady=5, padx=10, fill="x")

    def show_help_menu(self):
        """Shows the Help menu with information."""
        help_menu = ctk.CTkToplevel(self)
        help_menu.title("Help")
        help_menu.geometry("300x200")
        help_menu.resizable(False, False)
        help_menu.geometry("+310+50")

        # Bring window to front
        help_menu.transient(self)
        help_menu.lift()
        help_menu.focus_set()
        help_menu.attributes("-topmost", True)
        help_menu.after(100, lambda: help_menu.attributes("-topmost", False))

        help_text = ctk.CTkTextbox(help_menu)
        help_text.pack(pady=10, padx=10, fill="both", expand=True)
        help_text.insert("0.0",
            "Hamid PY Engine V1.4\n\n"
            "Controls:\n"
            "- Right-click + drag: Rotate camera\n"
            "- WASD: Move camera\n"
            "- Space/Shift: Move up/down\n"
            "- T: Translate mode\n"
            "- R: Rotate mode\n"
            "- Left-click: Select objects\n"
            "- Drag gizmo handles to transform\n\n"
            "File Format: .hamidmap (TOML)"
        )
        help_text.configure(state="disabled")

    def create_hierarchy_widgets(self):
        """Creates the hierarchy panel widgets."""
        self.hierarchy_buttons = []  # Store references to hierarchy buttons
        self.update_hierarchy_list()

    def update_hierarchy_list(self):
        """Updates the hierarchy list with current objects in the scene."""
        # Clear existing buttons
        for button in self.hierarchy_buttons:
            button.destroy()
        self.hierarchy_buttons.clear()

        # Add buttons for each object in the scene
        if hasattr(self.gl_frame, 'model_draw_list'):
            for i, obj in enumerate(self.gl_frame.model_draw_list):
                obj_name = obj.get('name', f"Object_{i}")

                # Create button for this object
                obj_button = ctk.CTkButton(
                    self.hierarchy_frame,
                    text=obj_name,
                    command=lambda idx=i: self.select_object_from_hierarchy(idx),
                    anchor="w",
                    height=30
                )
                obj_button.pack(fill="x", padx=5, pady=2)
                self.hierarchy_buttons.append(obj_button)

        # Update button appearances based on selection
        self.update_hierarchy_selection()

    def update_hierarchy_selection(self):
        """Updates the visual appearance of hierarchy buttons based on current selection."""
        if hasattr(self.gl_frame, 'selected_part_index'):
            selected_index = self.gl_frame.selected_part_index

            for i, button in enumerate(self.hierarchy_buttons):
                if i == selected_index:
                    # Highlight selected object
                    button.configure(fg_color=("#3B8ED0", "#1F6AA5"))
                else:
                    # Normal appearance
                    button.configure(fg_color=("gray75", "gray25"))

    def select_object_from_hierarchy(self, index):
        """Selects an object when clicked in the hierarchy list."""
        if hasattr(self.gl_frame, 'model_draw_list') and 0 <= index < len(self.gl_frame.model_draw_list):
            self.gl_frame.selected_part_index = index
            self.gl_frame._update_gizmo_collision_meshes()
            self.gl_frame._update_properties_panel()
            self.update_hierarchy_selection()
            self.gl_frame.focus_set()
            print(f"Selected object from hierarchy: {index}")

    def show_window_menu(self):
        """Shows the Window menu with options for various editor windows."""
        window_menu = ctk.CTkToplevel(self)
        window_menu.title("Window")
        window_menu.geometry("220x100")
        window_menu.resizable(False, False)

        # Position menu appropriately
        window_menu.geometry("+460+50")

        window_menu.transient(self)
        window_menu.lift()
        window_menu.focus_set()
        window_menu.attributes("-topmost", True)
        window_menu.after(100, lambda: window_menu.attributes("-topmost", False))

        # Environment Settings
        env_button = ctk.CTkButton(window_menu, text="Environment Settings", command=self.open_environment_settings)
        env_button.pack(pady=5, padx=10, fill="x")

    def open_environment_settings(self):
        """Opens a window to control fog and other environmental effects."""
        env_window = ctk.CTkToplevel(self)
        env_window.title("Environment Settings")
        env_window.geometry("350x200")
        env_window.resizable(False, False)
        env_window.geometry("+500+200")

        env_window.transient(self)
        env_window.lift()
        env_window.focus_set()

        title_label = ctk.CTkLabel(env_window, text="Atmospheric Fog", font=ctk.CTkFont(size=14, weight="bold"))
        title_label.pack(pady=(10, 15))

        # Fog Density Slider
        ctk.CTkLabel(env_window, text="Fog Density").pack(padx=20, anchor="w")
        density_slider = ctk.CTkSlider(env_window, from_=0.0, to=0.01, number_of_steps=100,
                                       command=lambda v: setattr(self, 'fog_density', v))
        density_slider.set(self.fog_density)
        density_slider.pack(pady=(0, 10), padx=20, fill="x")

        # Fog Gradient Slider
        ctk.CTkLabel(env_window, text="Fog Gradient").pack(padx=20, anchor="w")
        gradient_slider = ctk.CTkSlider(env_window, from_=0.5, to=5.0, number_of_steps=90,
                                        command=lambda v: setattr(self, 'fog_gradient', v))
        gradient_slider.set(self.fog_gradient)
        gradient_slider.pack(pady=(0, 10), padx=20, fill="x")

    def _on_paint_mode_change(self, slot_index, new_mode):
        """Callback to handle UI changes when switching between Color/Texture mode."""
        if self.gl_frame.selected_part_index is None: return
        selected_obj = self.gl_frame.model_draw_list[self.gl_frame.selected_part_index]
        if not self._is_terrain_object(selected_obj): return

        terrain_props = selected_obj.get('terrain_properties')
        if not terrain_props: return

        # --- 1. Update the data model ---
        if 'slot_modes' not in terrain_props:
            terrain_props['slot_modes'] = ['color', 'color', 'color']
        terrain_props['slot_modes'][slot_index] = new_mode.lower()

        # If switching back to color mode, ensure the texture is cleared
        if new_mode == "Color":
            terrain_props['texture_files'][slot_index] = None
            # This call clears the actual texture from the GPU
            self.gl_frame.set_terrain_texture(slot_index, None)

        print(f"Set layer {slot_index + 1} to {new_mode} mode.")

        # --- 2. Refresh the entire UI from the data model ---
        # This ensures the button states are always correct based on the current mode.
        self._update_terrain_editor_ui(selected_obj)

    def _update_terrain_editor_ui(self, terrain_obj):
        """Updates the terrain editor UI to reflect the properties of the selected terrain."""
        if not hasattr(self, 'paint_mode_buttons') or not terrain_obj:
            return

        props = terrain_obj.get('terrain_properties', {})
        slot_modes = props.get('slot_modes', ['color', 'color', 'color'])
        texture_files = props.get('texture_files', [None, None, None])

        for i in range(3):
            mode = slot_modes[i]
            self.paint_mode_buttons[i].set(mode.capitalize())

            if mode == 'color':
                self.color_buttons[i].configure(state="normal")
                self.texture_buttons[i].configure(state="disabled")
            else: # texture
                self.color_buttons[i].configure(state="disabled")
                self.texture_buttons[i].configure(state="normal")

            # Update texture file label
            if texture_files[i]:
                self.texture_file_labels[i].configure(text=os.path.basename(texture_files[i]))
            else:
                self.texture_file_labels[i].configure(text="No Texture Loaded")

    def choose_terrain_slot_color(self, slot_index):
        import tkinter.colorchooser as colorchooser

        if not (0 <= slot_index < 3): return

        selected_obj = None
        if self.gl_frame.selected_part_index is not None:
            selected_obj = self.gl_frame.model_draw_list[self.gl_frame.selected_part_index]

        if not selected_obj or not selected_obj.get('is_terrain'):
            print("Please select a terrain object before setting colors.")
            return

        terrain_props = selected_obj.get('terrain_properties')
        if not terrain_props: return

        initial_color = tuple(int(c * 255) for c in terrain_props['slot_colors'][slot_index][:3])
        color_choice = colorchooser.askcolor(color=initial_color, title=f"Choose Color for Slot {slot_index + 1}")

        if color_choice and color_choice[0]:
            new_color_rgb = [c / 255.0 for c in color_choice[0]]
            terrain_props['slot_colors'][slot_index] = new_color_rgb + [1.0] # Add alpha
            print(f"Set color for slot {slot_index + 1} to {terrain_props['slot_colors'][slot_index]}")

    def update_smooth_strength(self, value):
        """Update terrain smooth strength."""
        strength = float(value)
        # No direct setting on gl_frame needed, value is read on use
        self.smooth_strength_value_label.configure(text=f"{strength:.2f}")

    def update_paint_strength(self, value):
        """Update terrain paint strength."""
        strength = float(value)
        self.paint_strength_value_label.configure(text=f"{strength:.2f}")

    def load_terrain_texture(self, slot_index):
        if not (0 <= slot_index < 3): return

        selected_obj = None
        if self.gl_frame.selected_part_index is not None:
            selected_obj = self.gl_frame.model_draw_list[self.gl_frame.selected_part_index]

        if not selected_obj or not selected_obj.get('is_terrain'):
            print("Please select a terrain object before loading textures.")
            return

        filepath = filedialog.askopenfilename(
            title=f"Select Texture for Slot {slot_index + 1}",
            filetypes=(("Image Files", "*.png;*.jpg;*.jpeg"), ("All files", "*.*"))
        )
        if filepath:
            terrain_props = selected_obj.get('terrain_properties')
            if not terrain_props: return

            # Initialize missing keys if they don't exist
            if 'texture_files' not in terrain_props:
                terrain_props['texture_files'] = [None, None, None]
            if 'slot_colors' not in terrain_props:
                terrain_props['slot_colors'] = [[0.2, 0.6, 0.2, 1.0], [0.5, 0.5, 0.5, 1.0], [0.6, 0.4, 0.2, 1.0]]
            if 'slot_modes' not in terrain_props:
                terrain_props['slot_modes'] = ['color', 'color', 'color']
            if 'blend_weights' not in terrain_props:
                num_vertices = selected_obj['vertices'].shape[0]
                blend_weights = np.zeros((num_vertices, 3), dtype=np.float32)
                blend_weights[:, 0] = 1.0
                terrain_props['blend_weights'] = blend_weights

            try:
                # Store the filepath for saving the scene
                terrain_props['texture_files'][slot_index] = filepath
                filename = os.path.basename(filepath)
                self.texture_file_labels[slot_index].configure(text=filename)

                # Load the image using PIL
                with Image.open(filepath) as pil_image:
                    # Pass the PIL image object to the GL frame to create the texture
                    self.gl_frame.set_terrain_texture(slot_index, pil_image)

                print(f"Loaded texture for slot {slot_index + 1} from {filepath}")

            except Exception as e:
                print(f"Error loading texture file: {e}")
                # If loading fails, clear the texture reference
                if 'texture_files' in terrain_props:
                    terrain_props['texture_files'][slot_index] = None
                self.gl_frame.set_terrain_texture(slot_index, None)
                if hasattr(self, 'texture_file_labels') and slot_index < len(self.texture_file_labels):
                    self.texture_file_labels[slot_index].configure(text="Load Failed")

    def choose_sun_color(self):
        """Opens color picker for sun color."""
        if not self.sun_visible:
            print("Cannot change sun color when sun is disabled")
            return

        import tkinter.colorchooser as colorchooser

        # Convert current color to hex for color picker
        current_rgb = tuple(int(c * 255) for c in self.sun_color[:3])
        current_hex = f"#{current_rgb[0]:02x}{current_rgb[1]:02x}{current_rgb[2]:02x}"

        color = colorchooser.askcolor(color=current_hex, title="Choose Sun Color")
        if color[0]:  # If user didn't cancel
            # Convert RGB (0-255) to float (0-1)
            self.sun_color = [c/255.0 for c in color[0]] + [1.0]  # Add alpha
            print(f"Sun color changed to: {self.sun_color}")

    def choose_sky_color(self):
        """Opens color picker for sky color."""
        import tkinter.colorchooser as colorchooser

        # Convert current color to hex for color picker
        current_rgb = tuple(int(c * 255) for c in self.sky_color[:3])
        current_hex = f"#{current_rgb[0]:02x}{current_rgb[1]:02x}{current_rgb[2]:02x}"

        color = colorchooser.askcolor(color=current_hex, title="Choose Sky Color")
        if color[0]:  # If user didn't cancel
            # Convert RGB (0-255) to float (0-1)
            self.sky_color = [c/255.0 for c in color[0]] + [1.0]  # Add alpha
            print(f"Sky color changed to: {self.sky_color}")
            # Sky color will be applied automatically in the next frame render
            # Also update fog color if in auto mode
            # Rendering will be handled by animate_task automatically

    def choose_halo_color(self):
        """Opens color picker for halo color."""
        if not self.sun_visible:
            print("Cannot change halo color when sun is disabled")
            return

        import tkinter.colorchooser as colorchooser

        # Convert current color to hex for color picker
        current_rgb = tuple(int(c * 255) for c in self.halo_color[:3])
        current_hex = f"#{current_rgb[0]:02x}{current_rgb[1]:02x}{current_rgb[2]:02x}"

        color = colorchooser.askcolor(color=current_hex, title="Choose Halo Color")
        if color[0]:  # If user didn't cancel
            # Convert RGB (0-255) to float (0-1), keep original alpha
            self.halo_color = [c/255.0 for c in color[0]] + [self.halo_color[3]]  # Keep alpha
            print(f"Halo color changed to: {self.halo_color}")



    def toggle_sun_visibility(self):
        """Toggle sun and halo visibility and update button states."""
        try:
            # Get sun visibility state safely
            if hasattr(self, 'sun_visible_var') and self.sun_visible_var is not None:
                new_state = self.sun_visible_var.get()
                print(f"DEBUG: Checkbox state changed to: {new_state}")
                self.sun_visible = new_state
            else:
                # If checkbox var doesn't exist, keep current state
                self.sun_visible = getattr(self, 'sun_visible', True)
                print(f"Warning: sun_visible_var not available, using current state: {self.sun_visible}")

            print(f"DEBUG: Sun visibility is now: {self.sun_visible}")

            # Update button states based on sun visibility
            if self.sun_visible:
                # Enable sun and halo color buttons
                if hasattr(self, 'sun_color_button'):
                    self.sun_color_button.configure(state="normal")
                if hasattr(self, 'halo_color_button'):
                    self.halo_color_button.configure(state="normal")
                print("Sun and halo enabled")
            else:
                # Disable sun and halo color buttons
                if hasattr(self, 'sun_color_button'):
                    self.sun_color_button.configure(state="disabled")
                if hasattr(self, 'halo_color_button'):
                    self.halo_color_button.configure(state="disabled")
                print("Sun and halo disabled")

            # Force redraw to update the scene
            if hasattr(self, 'gl_frame') and self.gl_frame:
                # Rendering will be handled by animate_task automatically
                pass

        except Exception as e:
            print(f"Error toggling sun visibility: {e}")
            import traceback
            traceback.print_exc()
            # Reset to safe state
            self.sun_visible = True

    def _initialize_sun_button_states(self):
        """Initialize sun and halo button states based on sun visibility."""
        try:
            print(f"Initializing sun button states. sun_visible: {self.sun_visible}")

            # Set initial checkbox state if checkbox exists
            if hasattr(self, 'sun_visible_var') and self.sun_visible_var is not None:
                self.sun_visible_var.set(self.sun_visible)
                print(f"Set checkbox to: {self.sun_visible}")

            # Update button states
            if hasattr(self, 'sun_color_button') and hasattr(self, 'halo_color_button'):
                self.toggle_sun_visibility()
            else:
                print("Sun/halo buttons not ready yet")

        except Exception as e:
            print(f"Warning: Could not initialize sun button states: {e}")
            import traceback
            traceback.print_exc()

    def create_cube(self):
        """Creates a cube primitive."""
        cube_mesh = trimesh.creation.box(extents=[2.0, 2.0, 2.0])
        self._add_primitive_to_scene(cube_mesh, "Cube")

    def create_sphere(self):
        """Creates a sphere primitive."""
        # Submit heavy mesh creation to thread pool
        future = self.gl_frame.thread_pool.submit(self._create_sphere_threaded)
        self.after(50, lambda: self._check_primitive_creation_complete(future, "Sphere"))

    def _create_sphere_threaded(self):
        """Create sphere mesh in background thread."""
        try:
            return {'success': True, 'mesh': trimesh.creation.uv_sphere(radius=1.0, count=[32, 16])}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _check_primitive_creation_complete(self, future, primitive_name):
        """Check if primitive creation is complete and add to scene."""
        if future.done():
            try:
                result = future.result()
                if result['success']:
                    self._add_primitive_to_scene(result['mesh'], primitive_name)
                    print(f"{primitive_name} created successfully")
                else:
                    print(f"Error creating {primitive_name}: {result['error']}")
            except Exception as e:
                print(f"Error processing {primitive_name} creation: {e}")
        else:
            # Still processing, check again later
            self.after(50, lambda: self._check_primitive_creation_complete(future, primitive_name))

    def create_cone(self):
        """Creates a cone primitive."""
        cone_mesh = trimesh.creation.cone(radius=1.0, height=2.0, sections=32)
        self._add_primitive_to_scene(cone_mesh, "Cone")

    def create_cylinder(self):
        """Creates a cylinder primitive."""
        cylinder_mesh = trimesh.creation.cylinder(radius=1.0, height=2.0, sections=32)
        self._add_primitive_to_scene(cylinder_mesh, "Cylinder")

    def create_capsule(self):
        """Creates a capsule primitive that stands upright."""
        capsule_mesh = trimesh.creation.capsule(radius=0.5, height=2.0, count=[32, 16])
        self._add_primitive_to_scene(capsule_mesh, "Capsule")

    def create_enemy(self):
        """Creates an enemy capsule that stands upright and chases the player."""
        enemy_mesh = trimesh.creation.capsule(radius=0.5, height=2.0, count=[32, 16])
        self._add_enemy_to_scene(enemy_mesh, "Enemy")

    def _add_primitive_to_scene(self, mesh, name):
        """Helper method to add a primitive mesh to the scene."""
        try:
            # Process the mesh for drawing
            identity_transform = np.eye(4, dtype=np.float32)
            self.gl_frame._process_mesh_for_drawing(mesh, identity_transform, name)

            # Get the newly added object and mark it as a primitive
            if self.gl_frame.model_draw_list:
                new_obj = self.gl_frame.model_draw_list[-1]
                new_obj['model_file'] = None  # Primitives don't have model files
                new_obj['is_primitive'] = True
                new_obj['primitive_type'] = name.lower()

                # Auto-select the newly created primitive
                self.gl_frame.selected_part_index = len(self.gl_frame.model_draw_list) - 1
                self.gl_frame.model_loaded = True
                self.gl_frame._update_gizmo_collision_meshes()
                self.gl_frame._update_properties_panel()

                # Update hierarchy
                self.update_hierarchy_list()

                # Refresh display
                # Rendering will be handled by animate_task automatically

                print(f"Created {name} primitive")

        except Exception as e:
            print(f"Error creating {name}: {e}")
            traceback.print_exc()

    def _add_enemy_to_scene(self, mesh, name):
        """Helper method to add an enemy capsule to the scene."""
        try:
            # Process the mesh for drawing
            identity_transform = np.eye(4, dtype=np.float32)
            self.gl_frame._process_mesh_for_drawing(mesh, identity_transform, name)

            # Get the newly added object and configure as enemy
            if self.gl_frame.model_draw_list:
                new_obj = self.gl_frame.model_draw_list[-1]
                new_obj['model_file'] = None  # Enemies don't have model files
                new_obj['is_primitive'] = True
                new_obj['primitive_type'] = name.lower()
                new_obj['is_enemy'] = True  # Mark as enemy

                # Set enemy properties
                new_obj['base_color_factor'] = [1.0, 0.0, 0.0, 1.0]  # Red color
                new_obj['enemy_speed'] = 1.0  # 1 m/s chase speed
                new_obj['enemy_target'] = None  # Will be set to player position

                # Set physics properties for enemy
                new_obj['physics_type'] = 'RigidBody'
                new_obj['physics_shape'] = 'Mesh'
                new_obj['mass'] = 1.0

                # Position enemy standing upright (90 degrees rotation)
                new_obj['rotation'] = np.array([np.pi/2, 0.0, 0.0], dtype=np.float32)  # 90 degrees on X axis
                new_obj['position'] = np.array([5.0, 1.0, 5.0], dtype=np.float32)  # Spawn away from origin

                # Auto-select the newly created enemy
                self.gl_frame.selected_part_index = len(self.gl_frame.model_draw_list) - 1
                self.gl_frame.model_loaded = True
                self.gl_frame._update_gizmo_collision_meshes()
                self.gl_frame._update_properties_panel()

                # Update hierarchy
                self.update_hierarchy_list()

                # Refresh display
                # Rendering will be handled by animate_task automatically

                print(f"Created {name} enemy")

        except Exception as e:
            print(f"Error creating {name}: {e}")
            traceback.print_exc()

    def open_terrain_editor(self):
        """Opens a tabbed terrain editor window with creation, sculpting, and painting tools."""
        terrain_window = ctk.CTkToplevel(self)
        terrain_window.title("Terrain Editor")
        terrain_window.geometry("500x700")
        terrain_window.resizable(False, False)
        terrain_window.geometry("+400+200")

        terrain_window.transient(self)
        terrain_window.lift()
        terrain_window.focus_set()
        terrain_window.attributes("-topmost", True)
        terrain_window.after(100, lambda: terrain_window.attributes("-topmost", False))

        def on_terrain_window_close():
            if hasattr(self, 'terrain_editing_var') and self.terrain_editing_var.get():
                self.terrain_editing_var.set(False)
                self.gl_frame.set_terrain_editing_mode(False)
                print("Terrain editing mode disabled (window closed)")
            terrain_window.destroy()

        terrain_window.protocol("WM_DELETE_WINDOW", on_terrain_window_close)

        title_label = ctk.CTkLabel(terrain_window, text="Terrain Editor", font=ctk.CTkFont(size=16, weight="bold"))
        title_label.pack(pady=(10, 5))

        self.terrain_editing_var = ctk.BooleanVar()
        editing_checkbox = ctk.CTkCheckBox(terrain_window, text="Enable Editing on Selected Terrain",
                                         variable=self.terrain_editing_var,
                                         command=self.toggle_terrain_editing)
        editing_checkbox.pack(pady=10, padx=20, fill="x")

        tab_view = ctk.CTkTabview(terrain_window, width=380)
        tab_view.pack(pady=10, padx=20, fill="both", expand=True)

        create_tab = tab_view.add("Create")
        sculpt_tab = tab_view.add("Sculpt")
        paint_tab = tab_view.add("Paint")

        self.terrain_tool_mode_var = ctk.StringVar(value="Sculpt")
        sculpt_sub_mode_var = ctk.StringVar(value="Sculpt")

        def on_tab_changed():
            current_tab = tab_view.get()
            if current_tab == "Sculpt":
                self.terrain_tool_mode_var.set(sculpt_sub_mode_var.get())
            elif current_tab == "Paint":
                self.terrain_tool_mode_var.set("Paint")
            print(f"Terrain tool mode changed to: {self.terrain_tool_mode_var.get()}")

        tab_view.configure(command=on_tab_changed)

        # --- 1. CREATE TAB ---
        size_frame = ctk.CTkFrame(create_tab)
        size_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(size_frame, text="X Size (km):").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.terrain_x_var = ctk.StringVar(value="1.0")
        ctk.CTkEntry(size_frame, textvariable=self.terrain_x_var, width=100).grid(row=0, column=1, padx=10, pady=5)
        ctk.CTkLabel(size_frame, text="Y Size (km):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.terrain_y_var = ctk.StringVar(value="1.0")
        ctk.CTkEntry(size_frame, textvariable=self.terrain_y_var, width=100).grid(row=1, column=1, padx=10, pady=5)
        ctk.CTkLabel(size_frame, text="Base Color:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.terrain_color = [0.4, 0.6, 0.3, 1.0]
        self.terrain_color_button = ctk.CTkButton(size_frame, text="Choose Color", command=self.choose_terrain_color)
        self.terrain_color_button.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        create_button = ctk.CTkButton(create_tab, text="Create New Terrain", command=lambda: self.create_terrain_plane(terrain_window))
        create_button.pack(pady=20, padx=10, fill="x")

        # --- 2. SCULPT TAB ---
        sculpting_frame = ctk.CTkFrame(sculpt_tab, fg_color="transparent")
        sculpting_frame.pack(pady=5, padx=5, fill="both", expand=True)
        tool_mode_button = ctk.CTkSegmentedButton(sculpting_frame, values=["Sculpt", "Smooth"], variable=sculpt_sub_mode_var, command=self.terrain_tool_mode_var.set)
        tool_mode_button.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(sculpting_frame, text="Brush Size:").pack(padx=10, pady=(10, 0), anchor="w")
        self.brush_size_var = ctk.DoubleVar(value=25.0)
        ctk.CTkSlider(sculpting_frame, from_=5.0, to=100.0, variable=self.brush_size_var, command=self.update_brush_size).pack(padx=10, fill="x")
        self.brush_size_value_label = ctk.CTkLabel(sculpting_frame, text="25.0")
        self.brush_size_value_label.pack(padx=10, anchor="e")
        ctk.CTkLabel(sculpting_frame, text="Sculpt Strength:").pack(padx=10, pady=(10, 0), anchor="w")
        self.brush_strength_var = ctk.DoubleVar(value=0.5)
        ctk.CTkSlider(sculpting_frame, from_=0.1, to=2.0, variable=self.brush_strength_var, command=self.update_brush_strength).pack(padx=10, fill="x")
        self.brush_strength_value_label = ctk.CTkLabel(sculpting_frame, text="0.5")
        self.brush_strength_value_label.pack(padx=10, anchor="e")
        ctk.CTkLabel(sculpting_frame, text="Smooth Strength:").pack(padx=10, pady=(10, 0), anchor="w")
        self.smooth_strength_var = ctk.DoubleVar(value=0.1)
        ctk.CTkSlider(sculpting_frame, from_=0.01, to=1.0, variable=self.smooth_strength_var, command=self.update_smooth_strength).pack(padx=10, fill="x")
        self.smooth_strength_value_label = ctk.CTkLabel(sculpting_frame, text="0.10")
        self.smooth_strength_value_label.pack(padx=10, anchor="e")
        instructions = "Left-click to raise terrain.\nShift + Left-click to lower."
        ctk.CTkLabel(sculpting_frame, text=instructions, justify="left").pack(pady=20, padx=10)

        # --- 3. PAINT TAB ---
        painting_frame = ctk.CTkFrame(paint_tab, fg_color="transparent")
        painting_frame.pack(pady=5, padx=5, fill="both", expand=True)

        ctk.CTkLabel(painting_frame, text="Paint Strength:").pack(padx=10, pady=(10, 0), anchor="w")
        self.paint_strength_var = ctk.DoubleVar(value=0.2)
        ctk.CTkSlider(painting_frame, from_=0.01, to=1.0, variable=self.paint_strength_var, command=self.update_paint_strength).pack(padx=10, fill="x")
        self.paint_strength_value_label = ctk.CTkLabel(painting_frame, text="0.20")
        self.paint_strength_value_label.pack(padx=10, anchor="e")

        slot_frame = ctk.CTkFrame(painting_frame)
        slot_frame.pack(pady=15, padx=10, fill="x")
        ctk.CTkLabel(slot_frame, text="Active Layer:").pack(side="left", padx=10)
        self.active_texture_slot = ctk.IntVar(value=0)
        ctk.CTkRadioButton(slot_frame, text="1", variable=self.active_texture_slot, value=0).pack(side="left", padx=5)
        ctk.CTkRadioButton(slot_frame, text="2", variable=self.active_texture_slot, value=1).pack(side="left", padx=5)
        ctk.CTkRadioButton(slot_frame, text="3", variable=self.active_texture_slot, value=2).pack(side="left", padx=5)

        # Store UI elements to be able to access them later
        self.paint_mode_buttons = []
        self.texture_buttons = []
        self.color_buttons = []
        self.texture_file_labels = []

        for i in range(3):
            layer_frame = ctk.CTkFrame(painting_frame)
            layer_frame.pack(pady=5, padx=10, fill="x", expand=True)
            layer_frame.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(layer_frame, text=f"Layer {i+1}").grid(row=0, column=0, padx=(10, 5), pady=5, sticky="w")

            mode_switch = ctk.CTkSegmentedButton(layer_frame, values=["Color", "Texture"],
                                                 command=lambda mode, idx=i: self._on_paint_mode_change(idx, mode))
            mode_switch.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            mode_switch.set("Color") # Default
            self.paint_mode_buttons.append(mode_switch)

            # Frame for action buttons
            action_frame = ctk.CTkFrame(layer_frame, fg_color="transparent")
            action_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=2, sticky="ew")
            action_frame.grid_columnconfigure(0, weight=1)
            action_frame.grid_columnconfigure(1, weight=1)

            color_btn = ctk.CTkButton(action_frame, text="Set Color", command=lambda idx=i: self.choose_terrain_slot_color(idx))
            color_btn.grid(row=0, column=0, padx=(0,2), sticky="ew")
            self.color_buttons.append(color_btn)

            tex_btn = ctk.CTkButton(action_frame, text="Load Texture...", command=lambda idx=i: self.load_terrain_texture(idx), state="disabled")
            tex_btn.grid(row=0, column=1, padx=(2,0), sticky="ew")
            self.texture_buttons.append(tex_btn)

            tex_label = ctk.CTkLabel(layer_frame, text="No Texture Loaded", font=("", 10), text_color="gray")
            tex_label.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 5))
            self.texture_file_labels.append(tex_label)

        # Update the UI based on the currently selected object, if any
        if self.gl_frame.selected_part_index is not None:
             selected_obj = self.gl_frame.model_draw_list[self.gl_frame.selected_part_index]
             if self._is_terrain_object(selected_obj):
                 self._update_terrain_editor_ui(selected_obj)

    def toggle_terrain_editing(self):
        """Toggle terrain editing mode on/off."""
        enabled = self.terrain_editing_var.get()

        if enabled:
            if (hasattr(self.gl_frame, 'selected_part_index') and
                self.gl_frame.selected_part_index is not None):

                selected_obj = self.gl_frame.model_draw_list[self.gl_frame.selected_part_index]

                if self._is_terrain_object(selected_obj):
                    self.gl_frame.set_terrain_editing_mode(True, selected_obj)
                    self._update_terrain_editor_ui(selected_obj) # Add this line
                    print("Terrain editing mode enabled")
                else:
                    print("Please select a terrain object first")
                    self.terrain_editing_var.set(False)
            else:
                print("Please select a terrain object first")
                self.terrain_editing_var.set(False)
        else:
            self.gl_frame.set_terrain_editing_mode(False)
            print("Terrain editing mode disabled")

    def update_brush_size(self, value):
        """Update terrain brush size."""
        size = float(value)
        self.gl_frame.set_terrain_brush_size(size)
        self.brush_size_value_label.configure(text=f"{size:.1f}")

    def update_brush_strength(self, value):
        """Update terrain brush strength."""
        strength = float(value)
        self.gl_frame.set_terrain_brush_strength(strength)
        self.brush_strength_value_label.configure(text=f"{strength:.1f}")

    def _is_terrain_object(self, obj):
        """Check if an object is a terrain."""
        # Check for explicit terrain marking
        if obj.get('is_terrain', False):
            return True

        # Fallback: check if object has terrain-like properties
        if 'vertices' not in obj:
            return False

        vertices = obj['vertices']
        if len(vertices) == 0:
            return False

        # Check if mesh is relatively flat (terrain characteristic)
        y_range = np.max(vertices[:, 1]) - np.min(vertices[:, 1])
        x_range = np.max(vertices[:, 0]) - np.min(vertices[:, 0])
        z_range = np.max(vertices[:, 2]) - np.min(vertices[:, 2])

        # If Y range is much smaller than X or Z range, it's likely terrain
        horizontal_range = max(x_range, z_range)
        if horizontal_range > 0 and y_range / horizontal_range < 0.1:
            return True

        return False

    def choose_terrain_color(self):
        """Opens color picker for terrain color."""
        import tkinter.colorchooser as colorchooser

        # Convert current color to hex for color picker
        current_rgb = tuple(int(c * 255) for c in self.terrain_color[:3])
        current_hex = f"#{current_rgb[0]:02x}{current_rgb[1]:02x}{current_rgb[2]:02x}"

        color = colorchooser.askcolor(color=current_hex, title="Choose Terrain Color")
        if color[0]:  # If user didn't cancel
            # Convert RGB (0-255) to float (0-1)
            self.terrain_color = [c/255.0 for c in color[0]] + [1.0]  # Add alpha
            print(f"Terrain color changed to: {self.terrain_color}")

    def update_physics_from_ui(self, *args):
        """Updates physics properties from UI controls."""
        if hasattr(self.gl_frame, 'selected_part_index') and self.gl_frame.selected_part_index is not None:
            selected_obj = self.gl_frame.model_draw_list[self.gl_frame.selected_part_index]

            # Update physics properties
            selected_obj['physics_type'] = self.physics_type_var.get()
            selected_obj['physics_shape'] = self.physics_shape_var.get()

            # Validate physics shape for object type
            if self._is_terrain_object(selected_obj) and selected_obj['physics_shape'] != '2DPlane':
                if selected_obj['physics_type'] != 'None':
                    print("Warning: Terrain objects can only use 2DPlane physics shape")
                    self.physics_shape_var.set('2DPlane')
                    selected_obj['physics_shape'] = '2DPlane'
            elif not self._is_terrain_object(selected_obj) and selected_obj['physics_shape'] == '2DPlane':
                if selected_obj['physics_type'] != 'None':
                    print("Warning: 3D objects cannot use 2DPlane physics shape")
                    self.physics_shape_var.set('Mesh')
                    selected_obj['physics_shape'] = 'Mesh'

            print(f"Physics updated: Type={selected_obj['physics_type']}, Shape={selected_obj['physics_shape']}")

    def update_mass_from_ui(self, *args):
        """Updates mass from UI control."""
        if hasattr(self.gl_frame, 'selected_part_index') and self.gl_frame.selected_part_index is not None:
            try:
                mass_value = float(self.mass_var.get())
                if mass_value < 0:
                    mass_value = 0.1  # Minimum mass
                    self.mass_var.set("0.1")

                selected_obj = self.gl_frame.model_draw_list[self.gl_frame.selected_part_index]
                selected_obj['mass'] = mass_value
                print(f"Mass updated to: {mass_value}")
            except ValueError:
                pass  # Invalid input, ignore



    def _is_terrain_editing_active(self):
        """Check if terrain editing tools are currently active."""
        return (hasattr(self, 'terrain_editing_var') and
                self.terrain_editing_var is not None and
                self.terrain_editing_var.get())

    def toggle_physics(self):
        """Toggle physics simulation and FPS mode on/off (Unity-like Play button)."""
        if not self.physics_enabled:
            # Check if terrain editing tools are active
            if self._is_terrain_editing_active():
                # Show warning message
                import tkinter.messagebox as messagebox
                messagebox.showwarning(
                    "Cannot Start Game",
                    "Please first close editing tools.\n\nTerrain sculpting tools are currently active. "
                    "Close the terrain editor window or disable terrain editing mode before starting the game."
                )
                print("Cannot start game: Terrain editing tools are active")
                return

            # Start physics and FPS mode
            self._backup_scene()
            self._backup_camera()
            self._initialize_physics()
            self._enter_fps_mode()
            self.physics_enabled = True
            self.fps_mode = True
            self.play_button.configure(text="Stop", fg_color="#D83C3C")
            print("Game mode started - FPS Controller active")
        else:
            # Stop physics and FPS mode, restore scene
            self.physics_enabled = False
            self.fps_mode = False
            self._restore_scene()
            self._restore_camera()
            self._exit_fps_mode()
            self.play_button.configure(text="Play", fg_color=("#3B8ED0", "#1F6AA5"))
            print("Edit mode restored - Free fly camera active")

    def _backup_scene(self):
        """Backup current scene state before physics."""
        self.scene_backup = []
        for obj in self.gl_frame.model_draw_list:
            backup_obj = {
                'position': obj['position'].copy(),
                'rotation': obj['rotation'].copy(),
                'scale': obj['scale'].copy()
            }
            self.scene_backup.append(backup_obj)

    def _restore_scene(self):
        """Restore scene from backup."""
        if self.scene_backup:
            for i, backup_obj in enumerate(self.scene_backup):
                if i < len(self.gl_frame.model_draw_list):
                    self.gl_frame.model_draw_list[i]['position'] = backup_obj['position'].copy()
                    self.gl_frame.model_draw_list[i]['rotation'] = backup_obj['rotation'].copy()
                    self.gl_frame.model_draw_list[i]['scale'] = backup_obj['scale'].copy()
            self.gl_frame._update_properties_panel()

    def _backup_camera(self):
        """Backup current camera state before FPS mode."""
        self.fps_camera_backup = {
            'position': self.gl_frame.camera_pos.copy(),
            'yaw': self.gl_frame.camera_yaw,
            'pitch': self.gl_frame.camera_pitch,
            'front': self.gl_frame.camera_front.copy(),
            'up': self.gl_frame.camera_up.copy(),
            'right': self.gl_frame.camera_right.copy(),
            'speed': self.gl_frame.camera_speed
        }

    def _restore_camera(self):
        """Restore camera from backup after FPS mode."""
        if self.fps_camera_backup:
            self.gl_frame.camera_pos = self.fps_camera_backup['position'].copy()
            self.gl_frame.camera_yaw = self.fps_camera_backup['yaw']
            self.gl_frame.camera_pitch = self.fps_camera_backup['pitch']
            self.gl_frame.camera_front = self.fps_camera_backup['front'].copy()
            self.gl_frame.camera_up = self.fps_camera_backup['up'].copy()
            self.gl_frame.camera_right = self.fps_camera_backup['right'].copy()
            self.gl_frame.camera_speed = self.fps_camera_backup['speed']
            self.gl_frame._update_camera_vectors()

    def _enter_fps_mode(self):
        """Enter FPS controller mode with mouse locking."""
        # Position player at ground level, slightly above
        self.gl_frame.camera_pos = np.array([0.0, 1.8, 0.0], dtype=np.float32)  # Eye level height
        self.gl_frame.camera_yaw = -90.0  # Look forward
        self.gl_frame.camera_pitch = 0.0  # Level view
        self.gl_frame.camera_speed = 5.0  # CS:GO-like movement speed
        self.gl_frame._update_camera_vectors()

        # Disable gizmos and editing
        self.gl_frame.selected_part_index = None
        self.gl_frame.gizmo_handle_meshes.clear()
        self.gl_frame._update_properties_panel()

        # Set FPS-specific controls
        self.gl_frame.fps_mouse_sensitivity = 0.1
        self.gl_frame.fps_movement_speed = 5.0
        self.gl_frame.fps_jump_velocity = 0.0
        self.gl_frame.fps_on_ground = True
        self.gl_frame.fps_gravity = -15.0

        # Initialize mouse locking
        self.gl_frame._init_fps_mouse_lock()

        print("FPS Controller: Use WASD to move, mouse to look, Space to jump, ESC to exit")

    def _exit_fps_mode(self):
        """Exit FPS controller mode and restore mouse."""
        # Re-enable editing capabilities
        self.gl_frame.fps_mouse_sensitivity = None

        # Restore mouse cursor and unlock
        self.gl_frame._exit_fps_mouse_lock()

        print("Free fly camera restored")

    def _initialize_physics(self):
        """Initialize physics objects for simulation."""
        self.physics_objects = []
        for i, obj in enumerate(self.gl_frame.model_draw_list):
            physics_type = obj.get('physics_type', 'None')
            if physics_type != 'None':
                mass = obj.get('mass', 1.0) if physics_type == 'RigidBody' else 0.0
                physics_obj = {
                    'index': i,
                    'type': physics_type,
                    'shape': obj.get('physics_shape', 'Cube'),
                    'position': obj['position'].copy(),
                    'velocity': np.array([0.0, 0.0, 0.0], dtype=np.float32),
                    'angular_velocity': np.array([0.0, 0.0, 0.0], dtype=np.float32),
                    'mass': mass,
                    'bounds': self._calculate_physics_bounds(obj),
                    'center_of_mass': self._calculate_center_of_mass(obj),
                    'stability_factor': self._calculate_stability_factor(obj, mass),
                    'original_vertices': obj['vertices'].copy()  # Store original vertices for collision
                }
                self.physics_objects.append(physics_obj)

        self.last_physics_time = time.time()
        # Start physics update loop
        self.after(16, self._update_physics)  # ~60 FPS

    def _calculate_physics_bounds(self, obj):
        """Calculate physics bounds for collision detection with proper transform."""
        vertices = obj['vertices']
        scale = obj['scale']
        rotation = obj['rotation']
        position = obj['position']

        # Create transformation matrix
        transform_matrix = self._create_transform_matrix(position, rotation, scale)

        # Apply full transformation to vertices
        vertices_homogeneous = np.column_stack([vertices, np.ones(len(vertices))])
        transformed_vertices = (transform_matrix @ vertices_homogeneous.T).T[:, :3]

        # Calculate bounding box
        min_bounds = np.min(transformed_vertices, axis=0)
        max_bounds = np.max(transformed_vertices, axis=0)

        physics_shape = obj.get('physics_shape', 'Cube')

        bounds = {
            'min': min_bounds,
            'max': max_bounds,
            'center': (min_bounds + max_bounds) * 0.5,
            'size': max_bounds - min_bounds,
            'shape': physics_shape,
            'transform_matrix': transform_matrix,
            'rotation': rotation.copy(),
            'scale': scale.copy()
        }

        # Add shape-specific data for realistic physics with proper scaling
        if physics_shape == 'Sphere':
            # For sphere, use maximum scale component
            max_scale = np.max(scale)
            original_radius = np.max(np.max(vertices, axis=0) - np.min(vertices, axis=0)) * 0.5
            bounds['radius'] = original_radius * max_scale
        elif physics_shape == 'Cylinder' or physics_shape == 'Capsule':
            # For cylinder, scale radius by XZ scale, height by Y scale
            original_size = np.max(vertices, axis=0) - np.min(vertices, axis=0)
            bounds['radius'] = max(original_size[0], original_size[2]) * 0.5 * max(scale[0], scale[2])
            bounds['height'] = original_size[1] * scale[1]
        elif physics_shape == 'Mesh':
            # Store actual mesh data for precise collision
            bounds['mesh_vertices'] = transformed_vertices
            bounds['mesh_faces'] = obj['faces']
            bounds['mesh_normals'] = obj.get('normals', None)

        return bounds

    def _create_transform_matrix(self, position, rotation, scale):
        """Create a 4x4 transformation matrix from position, rotation, and scale."""
        # Create rotation matrices for each axis
        rx, ry, rz = rotation

        # Rotation around X axis
        cos_x, sin_x = np.cos(rx), np.sin(rx)
        rot_x = np.array([
            [1, 0, 0, 0],
            [0, cos_x, -sin_x, 0],
            [0, sin_x, cos_x, 0],
            [0, 0, 0, 1]
        ])

        # Rotation around Y axis
        cos_y, sin_y = np.cos(ry), np.sin(ry)
        rot_y = np.array([
            [cos_y, 0, sin_y, 0],
            [0, 1, 0, 0],
            [-sin_y, 0, cos_y, 0],
            [0, 0, 0, 1]
        ])

        # Rotation around Z axis
        cos_z, sin_z = np.cos(rz), np.sin(rz)
        rot_z = np.array([
            [cos_z, -sin_z, 0, 0],
            [sin_z, cos_z, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

        # Scale matrix
        scale_matrix = np.array([
            [scale[0], 0, 0, 0],
            [0, scale[1], 0, 0],
            [0, 0, scale[2], 0],
            [0, 0, 0, 1]
        ])

        # Translation matrix
        trans_matrix = np.array([
            [1, 0, 0, position[0]],
            [0, 1, 0, position[1]],
            [0, 0, 1, position[2]],
            [0, 0, 0, 1]
        ])

        # Combine transformations: Translation * Rotation * Scale
        rotation_matrix = rot_z @ rot_y @ rot_x
        return trans_matrix @ rotation_matrix @ scale_matrix

    def _calculate_center_of_mass(self, obj):
        """Calculate center of mass for realistic physics."""
        vertices = obj['vertices']
        # For simplicity, use geometric center weighted by mass distribution
        center = np.mean(vertices, axis=0)

        # Adjust center based on object shape for realism
        shape = obj.get('physics_shape', 'Cube')
        if shape == 'Sphere':
            # Sphere has uniform mass distribution
            pass
        elif shape == 'Cube':
            # Cube center is geometric center
            pass
        elif shape == 'Cylinder':
            # Cylinder center is slightly lower
            center[1] -= 0.1
        elif shape == 'Cone':
            # Cone center of mass is lower due to base
            center[1] -= 0.3

        return center

    def _calculate_stability_factor(self, obj, mass):
        """Calculate how stable an object is (resistance to tipping)."""
        bounds = obj['vertices']
        min_bounds = np.min(bounds, axis=0)
        max_bounds = np.max(bounds, axis=0)
        size = max_bounds - min_bounds

        # Base stability on width vs height ratio and mass
        base_area = size[0] * size[2]  # X-Z plane area
        height = size[1]

        # Higher mass and wider base = more stable
        # Taller objects are less stable
        stability = (base_area * mass) / (height + 0.1)

        return min(stability, 10.0)  # Cap stability factor

    def _update_physics(self):
        """Update physics simulation."""
        if not self.physics_enabled:
            return

        current_time = time.time()
        dt = min(current_time - self.last_physics_time, 0.033)  # Cap at 30 FPS
        self.last_physics_time = current_time

        # Update rigid body physics with threading for many objects
        rigidbody_objects = [obj for obj in self.physics_objects if obj['type'] == 'RigidBody']

        if len(rigidbody_objects) > 6:  # Use threading for many objects
            # Submit physics calculations to thread pool
            futures = []
            for physics_obj in rigidbody_objects:
                future = self.thread_pool.submit(self._calculate_rigidbody_physics_threaded, physics_obj, dt)
                futures.append((future, physics_obj))

            # Collect results
            for future, physics_obj in futures:
                try:
                    result = future.result(timeout=0.016)  # 16ms timeout
                    if result:
                        physics_obj.update(result)
                except Exception as e:
                    print(f"Physics calculation timeout or error: {e}")
                    # Fall back to direct calculation
                    self._update_rigidbody_physics(physics_obj, dt)
        else:
            # Direct calculation for few objects
            for physics_obj in rigidbody_objects:
                self._update_rigidbody_physics(physics_obj, dt)

        # Check object-to-object collisions
        self._check_object_collisions()

        # Update enemy AI
        self._update_enemy_ai(dt)

        # Apply physics results to scene objects
        for physics_obj in self.physics_objects:
            scene_obj = self.gl_frame.model_draw_list[physics_obj['index']]
            scene_obj['position'] = physics_obj['position'].copy()

            # Update bounds for next frame
            physics_obj['bounds'] = self._calculate_physics_bounds(scene_obj)

        # Continue physics loop
        self.after(16, self._update_physics)

    def _update_enemy_ai(self, dt):
        """Update enemy AI to chase the player using physics forces."""
        if not self.fps_mode:
            return  # Only chase when in FPS mode

        player_position = self.gl_frame.camera_pos

        # Update all enemies through physics system
        for physics_obj in self.physics_objects:
            scene_obj = self.gl_frame.model_draw_list[physics_obj['index']]

            if scene_obj.get('is_enemy', False):
                enemy_pos = physics_obj['position']
                enemy_speed = scene_obj.get('enemy_speed', 1.0)

                # Calculate direction to player
                direction = player_position - enemy_pos
                distance = np.linalg.norm(direction)

                if distance > 0.5:  # Don't move if too close
                    # Normalize direction and apply force to physics velocity
                    direction = direction / distance

                    # Check if enemy can move in this direction (collision detection)
                    test_position = enemy_pos + direction * enemy_speed * dt * 2.0
                    if not self._check_enemy_collision(test_position, physics_obj):
                        # Apply force to physics object velocity (not position)
                        force = direction * enemy_speed * 2.0  # Multiply by 2 for stronger force
                        physics_obj['velocity'][0] = force[0]
                        physics_obj['velocity'][2] = force[2]

                        # Make enemy face the player (rotate towards movement direction)
                        if abs(direction[0]) > 0.01 or abs(direction[2]) > 0.01:
                            angle = np.arctan2(direction[0], direction[2])
                            scene_obj['rotation'][1] = angle
                    else:
                        # Stop if collision detected
                        physics_obj['velocity'][0] = 0
                        physics_obj['velocity'][2] = 0

                    # Keep enemy on ground (don't fly)
                    if physics_obj['velocity'][1] > 0:
                        physics_obj['velocity'][1] = 0
                else:
                    # Stop moving when close to player
                    physics_obj['velocity'][0] = 0
                    physics_obj['velocity'][2] = 0

    def _check_enemy_collision(self, new_position, enemy_physics_obj):
        """Check if enemy would collide with static objects at new position."""
        enemy_radius = 0.5  # Enemy capsule radius
        enemy_height = 2.0  # Enemy capsule height

        # Enemy bounding cylinder
        enemy_bottom = new_position[1] - enemy_height * 0.5
        enemy_top = new_position[1] + enemy_height * 0.5
        enemy_center_xz = np.array([new_position[0], new_position[2]])

        # Check collision with each static physics object
        for physics_obj in self.physics_objects:
            # Skip self and non-static objects
            if physics_obj == enemy_physics_obj or physics_obj['type'] != 'Static':
                continue

            obj_bounds = physics_obj['bounds']

            # Check Y overlap first (height collision)
            if enemy_bottom > obj_bounds['max'][1] or enemy_top < obj_bounds['min'][1]:
                continue  # No vertical overlap

            # Check XZ collision based on object shape
            if self._check_enemy_xz_collision(enemy_center_xz, enemy_radius, physics_obj):
                return True  # Collision detected

        return False  # No collision

    def _check_enemy_xz_collision(self, enemy_center_xz, enemy_radius, physics_obj):
        """Check XZ plane collision between enemy and physics object."""
        obj_bounds = physics_obj['bounds']
        obj_pos = physics_obj['position']
        shape = obj_bounds['shape']

        obj_center_xz = np.array([obj_pos[0], obj_pos[2]])

        if shape == 'Sphere':
            # Sphere collision
            obj_radius = obj_bounds.get('radius', np.max(obj_bounds['size']) * 0.5)
            distance = np.linalg.norm(enemy_center_xz - obj_center_xz)
            return distance < (enemy_radius + obj_radius)

        elif shape == 'Cylinder' or shape == 'Capsule':
            # Cylinder collision
            obj_radius = obj_bounds.get('radius', max(obj_bounds['size'][0], obj_bounds['size'][2]) * 0.5)
            distance = np.linalg.norm(enemy_center_xz - obj_center_xz)
            return distance < (enemy_radius + obj_radius)

        else:
            # Box collision (Cube, Mesh, Cone, etc.)
            # Expand bounding box by enemy radius
            expanded_min = obj_bounds['min'][[0, 2]] - enemy_radius
            expanded_max = obj_bounds['max'][[0, 2]] + enemy_radius

            return (enemy_center_xz[0] >= expanded_min[0] and
                    enemy_center_xz[0] <= expanded_max[0] and
                    enemy_center_xz[1] >= expanded_min[1] and
                    enemy_center_xz[1] <= expanded_max[1])

    @staticmethod
    @jit(nopython=True)
    def _apply_gravity(velocity, dt):
        """Apply gravity using Numba for performance."""
        gravity = -9.81
        velocity[1] += gravity * dt
        return velocity

    @staticmethod
    @jit(nopython=True)
    def _apply_gravity_with_mass(velocity, dt, mass):
        """Apply gravity with mass consideration using Numba."""
        gravity = -9.81
        # Heavier objects fall faster initially but reach same terminal velocity
        mass_factor = min(mass, 5.0)  # Cap mass effect
        velocity[1] += gravity * dt * (0.8 + mass_factor * 0.04)
        return velocity

    def _apply_instability_forces(self, physics_obj, dt):
        """Apply realistic instability and tipping forces based on mass and shape."""
        mass = physics_obj['mass']
        stability = physics_obj['stability_factor']
        bounds = physics_obj['bounds']

        # Check if object is on ground or near ground
        ground_contact = physics_obj['position'][1] <= (bounds['size'][1] * 0.5 + 0.1)

        if ground_contact:
            # Calculate tipping threshold based on stability
            tipping_threshold = stability * 0.1

            # Check for horizontal forces that could cause tipping
            horizontal_force = np.sqrt(physics_obj['velocity'][0]**2 + physics_obj['velocity'][2]**2)

            # Apply tipping if force exceeds stability
            if horizontal_force > tipping_threshold:
                # Calculate tipping direction
                tip_direction = np.array([physics_obj['velocity'][0], 0, physics_obj['velocity'][2]])
                tip_magnitude = horizontal_force / stability

                # Apply angular velocity for tipping/rolling
                cross_product = np.cross([0, 1, 0], tip_direction)
                physics_obj['angular_velocity'] += cross_product * tip_magnitude * dt * mass

                # Add random instability for realism
                if mass > 2.0:  # Heavy objects create more dramatic effects
                    instability = (mass - 2.0) * 0.1
                    physics_obj['angular_velocity'][0] += (np.random.random() - 0.5) * instability
                    physics_obj['angular_velocity'][2] += (np.random.random() - 0.5) * instability

            # Apply rolling resistance
            rolling_resistance = 0.02 * mass
            if abs(physics_obj['velocity'][0]) > 0.1:
                physics_obj['velocity'][0] *= (1.0 - rolling_resistance * dt)
            if abs(physics_obj['velocity'][2]) > 0.1:
                physics_obj['velocity'][2] *= (1.0 - rolling_resistance * dt)

        # Apply mass-based angular momentum
        if mass > 1.0:
            # Heavier objects maintain angular velocity longer
            momentum_factor = min(mass / 5.0, 2.0)
            physics_obj['angular_velocity'] *= (1.0 + momentum_factor * 0.01)

    def _update_rigidbody_physics(self, physics_obj, dt):
        """Update rigid body physics with realistic mass-based rolling and instability."""
        mass = physics_obj['mass']

        # Apply gravity scaled by mass
        gravity_force = mass * 9.81
        physics_obj['velocity'] = self._apply_gravity_with_mass(physics_obj['velocity'], dt, mass)

        # Apply air resistance for realism (lighter objects affected more)
        air_resistance = 0.98 + (mass * 0.001)  # Heavier objects less affected by air
        physics_obj['velocity'] *= air_resistance

        # Check for instability and apply tipping forces
        self._apply_instability_forces(physics_obj, dt)

        # Update position
        old_position = physics_obj['position'].copy()
        physics_obj['position'] += physics_obj['velocity'] * dt

        # Update angular velocity with mass-based damping
        angular_damping = 0.99 - (mass * 0.001)  # Heavier objects maintain rotation longer
        physics_obj['angular_velocity'] *= angular_damping

        # Realistic ground collision based on shape
        bounds = physics_obj['bounds']
        ground_y = 0.0

        collision_occurred = False

        if bounds['shape'] == 'Sphere':
            # Sphere collision
            sphere_bottom = physics_obj['position'][1] - bounds['radius']
            if sphere_bottom <= ground_y:
                physics_obj['position'][1] = ground_y + bounds['radius']
                collision_occurred = True
        elif bounds['shape'] == 'Cube':
            # Box collision
            box_bottom = physics_obj['position'][1] - bounds['size'][1] * 0.5
            if box_bottom <= ground_y:
                physics_obj['position'][1] = ground_y + bounds['size'][1] * 0.5
                collision_occurred = True
        elif bounds['shape'] == 'Cylinder' or bounds['shape'] == 'Capsule':
            # Cylinder/Capsule collision
            cyl_bottom = physics_obj['position'][1] - bounds['height'] * 0.5
            if cyl_bottom <= ground_y:
                physics_obj['position'][1] = ground_y + bounds['height'] * 0.5
                collision_occurred = True
        elif bounds['shape'] == 'Mesh':
            # Mesh collision (use bounding box for performance)
            mesh_bottom = bounds['min'][1]
            if mesh_bottom <= ground_y:
                offset = ground_y - mesh_bottom
                physics_obj['position'][1] += offset
                collision_occurred = True
        else:
            # Default box collision
            box_bottom = physics_obj['position'][1] - bounds['size'][1] * 0.5
            if box_bottom <= ground_y:
                physics_obj['position'][1] = ground_y + bounds['size'][1] * 0.5
                collision_occurred = True

        # Handle collision response
        if collision_occurred:
            mass = physics_obj['mass']

            # Mass-based material properties
            restitution = max(0.1, 0.5 - mass * 0.05)  # Heavier objects bounce less
            friction = min(0.9, 0.5 + mass * 0.05)     # Heavier objects have more friction

            # Vertical bounce with mass consideration
            if physics_obj['velocity'][1] < 0:
                bounce_velocity = -physics_obj['velocity'][1] * restitution
                physics_obj['velocity'][1] = bounce_velocity

                # Heavy objects create impact effects
                if mass > 3.0:
                    impact_force = mass * abs(physics_obj['velocity'][1])
                    # Add slight random bounce for heavy impacts
                    if impact_force > 5.0:
                        physics_obj['velocity'][0] += (np.random.random() - 0.5) * 0.2
                        physics_obj['velocity'][2] += (np.random.random() - 0.5) * 0.2

            # Horizontal friction with rolling
            horizontal_speed = np.sqrt(physics_obj['velocity'][0]**2 + physics_obj['velocity'][2]**2)

            if horizontal_speed > 0.1:
                # Apply friction
                physics_obj['velocity'][0] *= friction
                physics_obj['velocity'][2] *= friction

                # Convert horizontal motion to rolling (angular velocity)
                rolling_factor = (1.0 - friction) * mass * 0.1
                physics_obj['angular_velocity'][0] += physics_obj['velocity'][2] * rolling_factor
                physics_obj['angular_velocity'][2] -= physics_obj['velocity'][0] * rolling_factor

                # Heavy objects roll more dramatically
                if mass > 2.0:
                    roll_enhancement = (mass - 2.0) * 0.05
                    physics_obj['angular_velocity'][0] *= (1.0 + roll_enhancement)
                    physics_obj['angular_velocity'][2] *= (1.0 + roll_enhancement)

            # Mass-based instability on impact
            if mass > 1.5:
                instability = (mass - 1.5) * 0.1
                physics_obj['angular_velocity'][1] += (np.random.random() - 0.5) * instability

    def _check_object_collisions(self):
        """Check for collisions between physics objects."""
        rigidbody_objects = [obj for obj in self.physics_objects if obj['type'] == 'RigidBody']

        if len(rigidbody_objects) > 8:  # Use threading for many objects
            self._check_collisions_threaded(rigidbody_objects)
        else:
            self._check_collisions_direct(rigidbody_objects)

    def _check_collisions_direct(self, rigidbody_objects):
        """Direct collision checking for small object counts."""
        for i, obj1 in enumerate(rigidbody_objects):
            for j, obj2 in enumerate(self.physics_objects):
                if i >= j or obj2['type'] == 'None':
                    continue

                # Simple bounding box collision detection
                bounds1 = obj1['bounds']
                bounds2 = obj2['bounds']

                # Check if bounding boxes overlap
                if (bounds1['min'][0] <= bounds2['max'][0] and bounds1['max'][0] >= bounds2['min'][0] and
                    bounds1['min'][1] <= bounds2['max'][1] and bounds1['max'][1] >= bounds2['min'][1] and
                    bounds1['min'][2] <= bounds2['max'][2] and bounds1['max'][2] >= bounds2['min'][2]):

                    # Collision detected - apply separation and response
                    self._resolve_collision(obj1, obj2)

    def _check_collisions_threaded(self, rigidbody_objects):
        """Threaded collision checking for many objects."""
        # Split objects into chunks for parallel processing
        chunk_size = max(2, len(rigidbody_objects) // 4)
        chunks = [rigidbody_objects[i:i + chunk_size] for i in range(0, len(rigidbody_objects), chunk_size)]

        # Submit collision detection tasks
        futures = []
        for chunk in chunks:
            future = self.thread_pool.submit(self._detect_collisions_chunk, chunk, self.physics_objects)
            futures.append(future)

        # Collect collision results
        all_collisions = []
        for future in futures:
            try:
                collisions = future.result(timeout=0.008)  # 8ms timeout
                all_collisions.extend(collisions)
            except Exception as e:
                print(f"Collision detection timeout: {e}")

        # Resolve collisions on main thread
        for obj1, obj2 in all_collisions:
            self._resolve_collision(obj1, obj2)

    def _detect_collisions_chunk(self, chunk_objects, all_objects):
        """Detect collisions for a chunk of objects (thread-safe)."""
        collisions = []
        for obj1 in chunk_objects:
            for obj2 in all_objects:
                if obj1 is obj2 or obj2['type'] == 'None':
                    continue

                # Simple bounding box collision detection
                bounds1 = obj1['bounds']
                bounds2 = obj2['bounds']

                # Check if bounding boxes overlap
                if (bounds1['min'][0] <= bounds2['max'][0] and bounds1['max'][0] >= bounds2['min'][0] and
                    bounds1['min'][1] <= bounds2['max'][1] and bounds1['max'][1] >= bounds2['min'][1] and
                    bounds1['min'][2] <= bounds2['max'][2] and bounds1['max'][2] >= bounds2['min'][2]):

                    collisions.append((obj1, obj2))

        return collisions

    def _resolve_collision(self, obj1, obj2):
        """Resolve collision between two physics objects."""
        # Calculate separation vector
        pos1 = obj1['position']
        pos2 = obj2['position']
        separation = pos1 - pos2
        distance = np.linalg.norm(separation)

        if distance < 0.001:  # Avoid division by zero
            separation = np.array([1.0, 0.0, 0.0])
            distance = 1.0

        separation_unit = separation / distance

        # Calculate minimum separation distance based on shapes
        min_distance = self._get_collision_distance(obj1, obj2)

        if distance < min_distance:
            # Separate objects
            overlap = min_distance - distance
            separation_offset = separation_unit * (overlap * 0.5)

            if obj1['type'] == 'RigidBody':
                obj1['position'] += separation_offset
            if obj2['type'] == 'RigidBody':
                obj2['position'] -= separation_offset

            # Apply collision response (elastic collision)
            if obj1['type'] == 'RigidBody' and obj2['type'] == 'RigidBody':
                # Exchange velocities along collision normal
                v1_normal = np.dot(obj1['velocity'], separation_unit)
                v2_normal = np.dot(obj2['velocity'], separation_unit)

                # Simple elastic collision
                obj1['velocity'] -= separation_unit * v1_normal * 0.8
                obj2['velocity'] -= separation_unit * v2_normal * 0.8
                obj1['velocity'] += separation_unit * v2_normal * 0.8
                obj2['velocity'] += separation_unit * v1_normal * 0.8

    def _get_collision_distance(self, obj1, obj2):
        """Get minimum collision distance between two objects based on their shapes."""
        bounds1 = obj1['bounds']
        bounds2 = obj2['bounds']

        # Default to bounding box sizes
        size1 = np.max(bounds1['size']) * 0.5
        size2 = np.max(bounds2['size']) * 0.5

        # Adjust for specific shapes
        if bounds1['shape'] == 'Sphere':
            size1 = bounds1.get('radius', size1)
        if bounds2['shape'] == 'Sphere':
            size2 = bounds2.get('radius', size2)

        return size1 + size2

    def _generate_terrain_grid(self, x_size, y_size, resolution):
        """Generate a detailed grid mesh for terrain sculpting."""
        vertices_list = []
        texcoords_list = []
        faces_list = []

        # Create heightmap for terrain sculpting
        heightmap = np.zeros((resolution, resolution), dtype=np.float32)

        # Generate vertices in a grid pattern
        half_x = x_size / 2.0
        half_y = y_size / 2.0
        vertex_spacing_x = x_size / (resolution - 1) if resolution > 1 else x_size
        vertex_spacing_y = y_size / (resolution - 1) if resolution > 1 else y_size

        for row in range(resolution):
            for col in range(resolution):
                # Calculate world position
                x = col * vertex_spacing_x - half_x
                z = row * vertex_spacing_y - half_y
                y = heightmap[row, col]  # Start with flat terrain

                vertices_list.append([x, y, z])

                # Calculate UV coordinates
                u = col / (resolution - 1) if resolution > 1 else 0
                v = row / (resolution - 1) if resolution > 1 else 0
                texcoords_list.append([u, v])

                # Create faces (two triangles per quad)
                if row < resolution - 1 and col < resolution - 1:
                    # Current quad vertices
                    tl = row * resolution + col        # Top-left
                    tr = row * resolution + col + 1    # Top-right
                    bl = (row + 1) * resolution + col  # Bottom-left
                    br = (row + 1) * resolution + col + 1  # Bottom-right

                    # Two triangles per quad (counter-clockwise)
                    faces_list.extend([
                        [tl, bl, tr],  # First triangle
                        [tr, bl, br]   # Second triangle
                    ])

        vertices = np.array(vertices_list, dtype=np.float32)
        faces = np.array(faces_list, dtype=np.uint32)
        texcoords = np.array(texcoords_list, dtype=np.float32)

        # Calculate normals (all pointing up initially)
        normals = np.tile([0, 1, 0], (len(vertices), 1)).astype(np.float32)

        return vertices, faces, normals, texcoords, heightmap

    def _recreate_terrain_with_heightmap(self, x_size, y_size, resolution, saved_heightmap):
        """Recreate terrain grid with saved heightmap data."""
        vertices_list = []
        texcoords_list = []
        faces_list = []

        # Convert saved heightmap back to numpy array
        heightmap = np.array(saved_heightmap, dtype=np.float32)

        # Ensure heightmap has correct dimensions
        if heightmap.shape != (resolution, resolution):
            print(f"Warning: Heightmap shape {heightmap.shape} doesn't match resolution {resolution}")
            # Create new heightmap if dimensions don't match
            heightmap = np.zeros((resolution, resolution), dtype=np.float32)

        # Generate vertices using the saved heightmap
        half_x = x_size / 2.0
        half_y = y_size / 2.0
        vertex_spacing_x = x_size / (resolution - 1) if resolution > 1 else x_size
        vertex_spacing_y = y_size / (resolution - 1) if resolution > 1 else y_size

        for row in range(resolution):
            for col in range(resolution):
                # Calculate world position
                x = col * vertex_spacing_x - half_x
                z = row * vertex_spacing_y - half_y
                y = heightmap[row, col]  # Use saved height data

                vertices_list.append([x, y, z])

                # Calculate UV coordinates
                u = col / (resolution - 1) if resolution > 1 else 0
                v = row / (resolution - 1) if resolution > 1 else 0
                texcoords_list.append([u, v])

                # Create faces (two triangles per quad)
                if row < resolution - 1 and col < resolution - 1:
                    # Current quad vertices
                    tl = row * resolution + col        # Top-left
                    tr = row * resolution + col + 1    # Top-right
                    bl = (row + 1) * resolution + col  # Bottom-left
                    br = (row + 1) * resolution + col + 1  # Bottom-right

                    # Two triangles per quad (counter-clockwise)
                    faces_list.extend([
                        [tl, bl, tr],  # First triangle
                        [tr, bl, br]   # Second triangle
                    ])

        vertices = np.array(vertices_list, dtype=np.float32)
        faces = np.array(faces_list, dtype=np.uint32)
        texcoords = np.array(texcoords_list, dtype=np.float32)

        # Calculate normals (all pointing up initially - could be improved)
        normals = np.tile([0, 1, 0], (len(vertices), 1)).astype(np.float32)

        return vertices, faces, normals, texcoords, heightmap

    def create_terrain_plane(self, window):
        """Creates a detailed grid mesh terrain with specified dimensions for sculpting."""
        try:
            # Get dimensions in km and convert to meters (multiply by 1000)
            x_size = float(self.terrain_x_var.get()) * 1000.0
            y_size = float(self.terrain_y_var.get()) * 1000.0

            # Create detailed grid mesh for terrain sculpting (6x higher quality)
            resolution = 157  # Grid resolution for sculpting (157x157 = 24,649 vertices, ~49,152 triangles)
            vertices, faces, normals, texcoords, heightmap = self._generate_terrain_grid(x_size, y_size, resolution)

            # Store terrain-specific data for sculpting
            num_vertices = vertices.shape[0]
            blend_weights = np.zeros((num_vertices, 3), dtype=np.float32)
            blend_weights[:, 0] = 1.0  # Default to first slot

            terrain_properties = {
                'size_x': x_size,
                'size_y': y_size,
                'resolution': resolution,
                'heightmap': heightmap,
                'blend_weights': blend_weights,
                'texture_files': [None, None, None],
                'slot_colors': [[0.2, 0.6, 0.2, 1.0], [0.5, 0.5, 0.5, 1.0], [0.6, 0.4, 0.2, 1.0]],
                'slot_modes': ['color', 'color', 'color'],
                'vertex_spacing': x_size / (resolution - 1) if resolution > 1 else x_size
            }

            # Create terrain object data with sculpting support
            terrain_data = {
                'name': f"Terrain_{x_size/1000:.1f}x{y_size/1000:.1f}km",
                'vertices': vertices,
                'faces': faces,
                'normals': normals,
                'texcoords': texcoords,
                'position': np.array([0.0, 0.0, 0.0], dtype=np.float32),
                'rotation': np.array([0.0, 0.0, 0.0], dtype=np.float32),
                'scale': np.array([1.0, 1.0, 1.0], dtype=np.float32),
                'base_color_factor': self.terrain_color,  # Use selected terrain color
                'is_transparent': False,
                'vertex_colors': None,
                'pil_image_ref': None,
                'model_file': None,
                'terrain_properties': terrain_properties,  # Add terrain-specific data
                'is_terrain': True,  # Mark as terrain for identification
                'script_file': None  # Script file path (portable, relative)
            }

            # Add to scene
            self.gl_frame.model_draw_list.append(terrain_data)

            # Select the newly created terrain
            self.gl_frame.selected_part_index = len(self.gl_frame.model_draw_list) - 1
            self.gl_frame.model_loaded = True
            self.gl_frame._update_gizmo_collision_meshes()
            self.gl_frame._update_properties_panel()

            # Update hierarchy
            self.update_hierarchy_list()

            # Refresh display
            # Rendering will be handled by animate_task automatically

            print(f"Created terrain plane: {x_size/1000:.1f}km x {y_size/1000:.1f}km")

            # Close terrain editor window
            window.destroy()

        except ValueError:
            print("Error: Invalid terrain size values")
        except Exception as e:
            print(f"Error creating terrain: {e}")

    def create_properties_widgets(self):
        """Creates all the widgets for the right-side properties panel."""
        self.properties_frame.grid_columnconfigure(1, weight=1)

        # --- StringVars for real-time updates ---
        self.pos_x_var, self.pos_y_var, self.pos_z_var = ctk.StringVar(), ctk.StringVar(), ctk.StringVar()
        self.rot_x_var, self.rot_y_var, self.rot_z_var = ctk.StringVar(), ctk.StringVar(), ctk.StringVar()
        self.scale_x_var, self.scale_y_var, self.scale_z_var = ctk.StringVar(), ctk.StringVar(), ctk.StringVar()

        # --- Tracing vars to call update function ---
        for var in [self.pos_x_var, self.pos_y_var, self.pos_z_var,
                    self.rot_x_var, self.rot_y_var, self.rot_z_var,
                    self.scale_x_var, self.scale_y_var, self.scale_z_var]:
            var.trace_add("write", self.update_model_from_ui_callback)

        row = 0
        # --- Transform Header ---
        transform_label = ctk.CTkLabel(self.properties_frame, text="Transform", font=ctk.CTkFont(weight="bold"))
        transform_label.grid(row=row, column=0, columnspan=2, pady=(10, 5), sticky="w", padx=10)
        row += 1

        # --- Position ---
        ctk.CTkLabel(self.properties_frame, text="Position").grid(row=row, column=0, padx=10, pady=2, sticky="w")
        pos_frame = ctk.CTkFrame(self.properties_frame, fg_color="transparent")
        pos_frame.grid(row=row, column=1, padx=5, pady=2, sticky="ew")
        pos_frame.grid_columnconfigure((0,1,2), weight=1)
        self.pos_x_entry = ctk.CTkEntry(pos_frame, textvariable=self.pos_x_var, width=120); self.pos_x_entry.grid(row=0,column=0,padx=2)
        self.pos_y_entry = ctk.CTkEntry(pos_frame, textvariable=self.pos_y_var, width=120); self.pos_y_entry.grid(row=0,column=1,padx=2)
        self.pos_z_entry = ctk.CTkEntry(pos_frame, textvariable=self.pos_z_var, width=120); self.pos_z_entry.grid(row=0,column=2,padx=2)
        row += 1

        # --- Rotation ---
        ctk.CTkLabel(self.properties_frame, text="Rotation").grid(row=row, column=0, padx=10, pady=2, sticky="w")
        rot_frame = ctk.CTkFrame(self.properties_frame, fg_color="transparent")
        rot_frame.grid(row=row, column=1, padx=5, pady=2, sticky="ew")
        rot_frame.grid_columnconfigure((0,1,2), weight=1)
        self.rot_x_entry = ctk.CTkEntry(rot_frame, textvariable=self.rot_x_var, width=120); self.rot_x_entry.grid(row=0,column=0,padx=2)
        self.rot_y_entry = ctk.CTkEntry(rot_frame, textvariable=self.rot_y_var, width=120); self.rot_y_entry.grid(row=0,column=1,padx=2)
        self.rot_z_entry = ctk.CTkEntry(rot_frame, textvariable=self.rot_z_var, width=120); self.rot_z_entry.grid(row=0,column=2,padx=2)
        row += 1

        # --- Scale ---
        ctk.CTkLabel(self.properties_frame, text="Scale").grid(row=row, column=0, padx=10, pady=2, sticky="w")
        scale_frame = ctk.CTkFrame(self.properties_frame, fg_color="transparent")
        scale_frame.grid(row=row, column=1, padx=5, pady=2, sticky="ew")
        scale_frame.grid_columnconfigure((0,1,2), weight=1)
        self.scale_x_entry = ctk.CTkEntry(scale_frame, textvariable=self.scale_x_var, width=120); self.scale_x_entry.grid(row=0,column=0,padx=2)
        self.scale_y_entry = ctk.CTkEntry(scale_frame, textvariable=self.scale_y_var, width=120); self.scale_y_entry.grid(row=0,column=1,padx=2)
        self.scale_z_entry = ctk.CTkEntry(scale_frame, textvariable=self.scale_z_var, width=120); self.scale_z_entry.grid(row=0,column=2,padx=2)
        row += 1

        # --- Material Header ---
        material_label = ctk.CTkLabel(self.properties_frame, text="Material", font=ctk.CTkFont(weight="bold"))
        material_label.grid(row=row, column=0, columnspan=2, pady=(20, 5), sticky="w", padx=10)
        row += 1

        # --- Color ---
        self.color_r_label = ctk.CTkLabel(self.properties_frame, text="R: -"); self.color_r_label.grid(row=row, column=0, padx=10, pady=2, sticky="w")
        self.color_r_slider = ctk.CTkSlider(self.properties_frame, from_=0, to=1, command=self.update_model_from_ui_callback); self.color_r_slider.grid(row=row, column=1, padx=10, pady=5, sticky="ew"); row += 1

        self.color_g_label = ctk.CTkLabel(self.properties_frame, text="G: -"); self.color_g_label.grid(row=row, column=0, padx=10, pady=2, sticky="w")
        self.color_g_slider = ctk.CTkSlider(self.properties_frame, from_=0, to=1, command=self.update_model_from_ui_callback); self.color_g_slider.grid(row=row, column=1, padx=10, pady=5, sticky="ew"); row += 1

        self.color_b_label = ctk.CTkLabel(self.properties_frame, text="B: -"); self.color_b_label.grid(row=row, column=0, padx=10, pady=2, sticky="w")
        self.color_b_slider = ctk.CTkSlider(self.properties_frame, from_=0, to=1, command=self.update_model_from_ui_callback); self.color_b_slider.grid(row=row, column=1, padx=10, pady=5, sticky="ew"); row += 1

        # --- ADD THIS BLOCK FOR THE ALPHA SLIDER ---
        self.color_a_label = ctk.CTkLabel(self.properties_frame, text="A: -"); self.color_a_label.grid(row=row, column=0, padx=10, pady=2, sticky="w")
        self.color_a_slider = ctk.CTkSlider(self.properties_frame, from_=0, to=1, command=self.update_model_from_ui_callback); self.color_a_slider.grid(row=row, column=1, padx=10, pady=5, sticky="ew"); row += 1
        # --- END OF BLOCK TO ADD ---

        # --- Actions Header ---
        actions_label = ctk.CTkLabel(self.properties_frame, text="Actions", font=ctk.CTkFont(weight="bold"))
        actions_label.grid(row=row, column=0, columnspan=2, pady=(20, 5), sticky="w", padx=10)
        row += 1

        # --- Duplicate and Delete Buttons ---
        self.duplicate_button = ctk.CTkButton(self.properties_frame, text="Duplicate Object", command=self.duplicate_selected_object)
        self.duplicate_button.grid(row=row, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        row += 1

        self.delete_button = ctk.CTkButton(self.properties_frame, text="Delete Object", command=self.delete_selected_object, fg_color="#D83C3C", hover_color="#A82727")
        self.delete_button.grid(row=row, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        row += 1

        # --- Physics Header ---
        physics_label = ctk.CTkLabel(self.properties_frame, text="Physics", font=ctk.CTkFont(weight="bold"))
        physics_label.grid(row=row, column=0, columnspan=2, pady=(20, 5), sticky="w", padx=10)
        row += 1

        # Physics Type
        self.physics_type_var = ctk.StringVar(value="None")
        physics_type_label = ctk.CTkLabel(self.properties_frame, text="Physics Type:")
        physics_type_label.grid(row=row, column=0, padx=10, pady=2, sticky="w")

        physics_type_frame = ctk.CTkFrame(self.properties_frame, fg_color="transparent")
        physics_type_frame.grid(row=row, column=1, padx=5, pady=2, sticky="ew")

        self.physics_none_radio = ctk.CTkRadioButton(physics_type_frame, text="NONE", variable=self.physics_type_var, value="None", command=self.update_physics_from_ui)
        self.physics_none_radio.pack(side="top", padx=2, anchor="w")

        self.physics_static_radio = ctk.CTkRadioButton(physics_type_frame, text="STATIC", variable=self.physics_type_var, value="Static", command=self.update_physics_from_ui)
        self.physics_static_radio.pack(side="top", padx=2, anchor="w")

        self.physics_rigidbody_radio = ctk.CTkRadioButton(physics_type_frame, text="RIGID BODY", variable=self.physics_type_var, value="RigidBody", command=self.update_physics_from_ui)
        self.physics_rigidbody_radio.pack(side="top", padx=2, anchor="w")
        row += 1

        # Physics Shape
        self.physics_shape_var = ctk.StringVar(value="Cube")
        physics_shape_label = ctk.CTkLabel(self.properties_frame, text="Physics Shape:")
        physics_shape_label.grid(row=row, column=0, padx=10, pady=2, sticky="w")

        self.physics_shape_menu = ctk.CTkOptionMenu(self.properties_frame, variable=self.physics_shape_var,
                                                   values=["Cube", "Sphere", "Cylinder", "Cone", "Capsule", "Mesh", "2DPlane"],
                                                   command=self.update_physics_from_ui)
        self.physics_shape_menu.grid(row=row, column=1, padx=10, pady=2, sticky="ew")
        row += 1

        # Mass control
        self.mass_var = ctk.StringVar(value="1.0")
        mass_label = ctk.CTkLabel(self.properties_frame, text="Mass:")
        mass_label.grid(row=row, column=0, padx=10, pady=2, sticky="w")

        self.mass_entry = ctk.CTkEntry(self.properties_frame, textvariable=self.mass_var, width=120)
        self.mass_entry.grid(row=row, column=1, padx=10, pady=2, sticky="ew")
        self.mass_var.trace_add("write", self.update_mass_from_ui)
        row += 1

        # Store all interactive widgets to easily change their state
        self.interactive_widgets = [self.pos_x_entry, self.pos_y_entry, self.pos_z_entry,
                                    self.rot_x_entry, self.rot_y_entry, self.rot_z_entry,
                                    self.scale_x_entry, self.scale_y_entry, self.scale_z_entry,
                                    self.color_r_slider, self.color_g_slider, self.color_b_slider,
                                    # --- ADD self.color_a_slider TO THIS LIST ---
                                    self.color_a_slider,
                                    self.duplicate_button, self.delete_button,
                                    self.physics_none_radio, self.physics_static_radio, self.physics_rigidbody_radio,
                                    self.physics_shape_menu, self.mass_entry]

    def set_properties_state(self, state):
        """Enable or disable all widgets in the properties panel."""
        for widget in self.interactive_widgets:
            widget.configure(state=state)

    def update_model_from_ui_callback(self, *args):
        """Callback function triggered by UI changes."""
        self.gl_frame._update_transform_from_ui()

    def set_gizmo_mode(self, mode):
        print(f"Setting gizmo mode to: {mode}")
        self.gl_frame.set_gizmo_mode(mode)
        self.gl_frame.focus_set()

    def open_file_dialog(self):
        filepath = filedialog.askopenfilename(
            title="Select .glb or .gltf File",
            filetypes=((".glb files", "*.glb"), (".gltf files", "*.gltf"), ("All files", "*.*"))
        )
        if filepath:
            self.gl_frame.load_new_model(filepath)
            self.gl_frame.focus_set()

    def duplicate_selected_object(self):
        """Calls the duplicate method in the OpenGL frame."""
        self.gl_frame.duplicate_selected_part()
        self.gl_frame.focus_set()

    def delete_selected_object(self):
        """Calls the delete method in the OpenGL frame."""
        self.gl_frame.delete_selected_part()
        self.gl_frame.focus_set()



    def new_scene(self):
        """Creates a new empty scene."""
        self.gl_frame._cleanup_old_model_resources()
        self.update_hierarchy_list()
        print("New scene created.")

    def save_scene(self):
        """Saves the current scene to a .hamidmap TOML file."""
        if not self.gl_frame.model_draw_list:
            print("No objects in scene to save.")
            return

        filepath = filedialog.asksaveasfilename(
            title="Save Scene As",
            defaultextension=".hamidmap",
            filetypes=[("HamidMap files", "*.hamidmap"), ("All files", "*.*")]
        )
        if not filepath:
            return

        try:
            scene_data = {
                "scene_info": {"version": "1.4.0", "engine": "Hamid PY Engine V1.4"},
                "camera": {
                    "position": self.gl_frame.camera_pos.tolist(),
                    "yaw": self.gl_frame.camera_yaw,
                    "pitch": self.gl_frame.camera_pitch
                },
                "environment": {
                    "sun_color": self.sun_color, "sky_color": self.sky_color,
                    "halo_color": self.halo_color, "sun_visible": self.sun_visible,
                    "fog_density": self.fog_density, "fog_gradient": self.fog_gradient
                },
                "objects": []
            }

            for obj in self.gl_frame.model_draw_list:
                obj_data = {
                    "name": obj.get('name'), "model_file": obj.get('model_file'),
                    "transform": {
                        "position": obj['position'].tolist(),
                        "rotation": obj['rotation'].tolist(),
                        "scale": obj['scale'].tolist()
                    },
                    "material": {
                        "base_color": obj['base_color_factor'],
                        # --- ADD THIS LINE ---
                        "is_transparent": obj.get('is_transparent', False)
                    },
                    "physics": {
                        "type": obj.get('physics_type', 'None'),
                        "shape": obj.get('physics_shape', 'Cube'),
                        "mass": obj.get('mass', 1.0)
                    }
                }
                if obj.get('is_terrain'):
                    props = obj['terrain_properties']
                    obj_data["terrain_data"] = {
                        "is_terrain": True,
                        "size_x_km": props['size_x'] / 1000.0,
                        "size_y_km": props['size_y'] / 1000.0,
                        "resolution": props['resolution'],
                        "heightmap": props['heightmap'].tolist(),
                        "blend_weights": props['blend_weights'].tolist(),
                        "texture_files": props.get('texture_files'),
                        "slot_colors": props.get('slot_colors'),
                        "slot_modes": props.get('slot_modes')
                    }
                if obj.get('is_primitive'):
                    obj_data["primitive_data"] = {
                        # --- ADD THIS LINE ---
                        "is_primitive": True,
                        "type": obj.get('primitive_type'),
                        "is_enemy": obj.get('is_enemy', False),
                        "enemy_speed": obj.get('enemy_speed', 1.0)
                    }
                scene_data["objects"].append(obj_data)

            with open(filepath, 'w') as f:
                toml.dump(scene_data, f)
            print(f"Scene saved successfully to: {filepath}")

        except Exception as e:
            print(f"Error saving scene: {e}")
            traceback.print_exc()

    def load_scene(self):
        """Loads a scene from a .hamidmap TOML file."""
        filepath = filedialog.askopenfilename(
            title="Load Scene",
            filetypes=[("HamidMap files", "*.hamidmap"), ("All files", "*.*")]
        )
        if not filepath:
            return

        try:
            with open(filepath, 'r') as f:
                scene_data = toml.load(f)

            self.gl_frame._cleanup_old_model_resources()

            cam = scene_data.get("camera", {})
            self.gl_frame.camera_pos = np.array(cam.get("position", [0, 1, 5]), dtype=np.float32)
            self.gl_frame.camera_yaw = cam.get("yaw", -90.0)
            self.gl_frame.camera_pitch = cam.get("pitch", 0.0)
            self.gl_frame._update_camera_vectors()

            env = scene_data.get("environment", {})
            self.sun_color = env.get("sun_color", [1.0, 0.9, 0.7, 1.0])
            self.sky_color = env.get("sky_color", [0.6, 0.7, 0.9, 1.0])
            self.halo_color = env.get("halo_color", [1.0, 0.9, 0.7, 0.15])
            self.sun_visible = env.get("sun_visible", True)
            self.fog_density = env.get("fog_density", 0.003)
            self.fog_gradient = env.get("fog_gradient", 1.5)
            self.sun_visible_var.set(self.sun_visible)
            self.toggle_sun_visibility()

            if "objects" in scene_data:
                for obj_data in scene_data["objects"]:
                    self._load_object_from_data(obj_data)

            self.gl_frame.model_loaded = True
            self.update_hierarchy_list()
            self.gl_frame._update_properties_panel()
            print(f"Scene loaded successfully from: {filepath}")

        except Exception as e:
            print(f"Error loading scene: {e}")
            traceback.print_exc()

    def _load_object_from_data(self, obj_data):
        """Helper method to recreate an object from saved data."""
        try:
            # Check if this is terrain data
            terrain_data = obj_data.get('terrain_data')
            if terrain_data and terrain_data.get('is_terrain'):
                # Recreate terrain from saved data
                self._recreate_terrain_from_data(obj_data, terrain_data)
                return

            # Check if this is primitive data
            # --- CHANGE THIS LINE ---
            if 'primitive_data' in obj_data:
                # Recreate primitive from saved data
                self._recreate_primitive_from_data(obj_data, obj_data['primitive_data'])
                return

            model_file = obj_data.get('model_file')

            if model_file and os.path.exists(model_file):
                # Load the original model file
                print(f"Loading model from: {model_file}")

                # Use trimesh to load the model
                combined_mesh = trimesh.load(model_file, force='mesh', process=True)

                if isinstance(combined_mesh, trimesh.Trimesh) and not combined_mesh.is_empty:
                    # Process the mesh using existing method
                    identity_transform = np.eye(4, dtype=np.float32)
                    self.gl_frame._process_mesh_for_drawing(combined_mesh, identity_transform, obj_data.get('name', 'Loaded_Object'))

                    # Get the newly added object (last in list)
                    if self.gl_frame.model_draw_list:
                        new_obj = self.gl_frame.model_draw_list[-1]

                        # Apply saved transform and material properties
                        new_obj['position'] = np.array(obj_data['transform']['position'], dtype=np.float32)
                        new_obj['rotation'] = np.array(obj_data['transform']['rotation'], dtype=np.float32)
                        new_obj['scale'] = np.array(obj_data['transform']['scale'], dtype=np.float32)
                        new_obj['base_color_factor'] = obj_data['material']['base_color']
                        new_obj['is_transparent'] = obj_data['material'].get('is_transparent', False)
                        new_obj['model_file'] = model_file  # Store the model file path

                        # Restore physics properties
                        physics_data = obj_data.get('physics', {})
                        new_obj['physics_type'] = physics_data.get('type', 'None')
                        new_obj['physics_shape'] = physics_data.get('shape', 'Cube')
                        new_obj['mass'] = physics_data.get('mass', 1.0)

                        # Restore script file
                        script_file = obj_data.get('script_file')
                        new_obj['script_file'] = script_file

                        print(f"Successfully loaded and positioned object: {obj_data.get('name', 'Loaded_Object')}")
                else:
                    print(f"Warning: Could not load model from {model_file}")
            else:
                print(f"Warning: Model file not found or not specified: {model_file}")

        except Exception as e:
            print(f"Error loading object: {e}")
            traceback.print_exc()

    def _recreate_terrain_from_data(self, obj_data, terrain_data):
        """Recreate terrain from saved terrain data with heightmap and texture support."""
        try:
            x_size = terrain_data['size_x_km'] * 1000.0
            y_size = terrain_data['size_y_km'] * 1000.0
            resolution = terrain_data['resolution']

            vertices, faces, normals, texcoords, heightmap = self._recreate_terrain_with_heightmap(
                x_size, y_size, resolution, terrain_data['heightmap']
            )

            blend_weights = np.array(terrain_data['blend_weights'], dtype=np.float32)

            terrain_properties = {
                'size_x': x_size, 'size_y': y_size, 'resolution': resolution,
                'heightmap': heightmap, 'blend_weights': blend_weights,
                'texture_files': terrain_data.get('texture_files', [None, None, None]),
                'slot_colors': terrain_data.get('slot_colors', [[0.2,0.6,0.2,1],[0.5,0.5,0.5,1],[0.6,0.4,0.2,1]]),
                'slot_modes': terrain_data.get('slot_modes', ['color', 'color', 'color']),
                'vertex_spacing': x_size / (resolution - 1) if resolution > 1 else x_size
            }

            recreated_terrain = {
                'name': obj_data.get('name'),
                'vertices': vertices, 'faces': faces, 'normals': normals, 'texcoords': texcoords,
                'position': np.array(obj_data['transform']['position'], dtype=np.float32),
                'rotation': np.array(obj_data['transform']['rotation'], dtype=np.float32),
                'scale': np.array(obj_data['transform']['scale'], dtype=np.float32),
                'base_color_factor': obj_data['material']['base_color'],
                # --- CHANGE THIS LINE ---
                'is_transparent': obj_data['material'].get('is_transparent', False), 'vertex_colors': None, 'pil_image_ref': None,
                'model_file': None, 'terrain_properties': terrain_properties, 'is_terrain': True
            }

            physics_data = obj_data.get('physics', {})
            recreated_terrain.update({
                'physics_type': physics_data.get('type', 'None'),
                'physics_shape': physics_data.get('shape', '2DPlane'),
                'mass': physics_data.get('mass', 1.0)
            })

            self.gl_frame.model_draw_list.append(recreated_terrain)

            for i, filepath in enumerate(terrain_properties['texture_files']):
                if filepath and os.path.exists(filepath):
                    try:
                        with Image.open(filepath) as pil_image:
                            self.gl_frame.set_terrain_texture(i, pil_image.copy())
                        print(f"Reloaded texture for slot {i+1} from {filepath}")
                    except Exception as e:
                        print(f"Failed to reload texture from {filepath}: {e}")
                else:
                    self.gl_frame.set_terrain_texture(i, None)

            print(f"Successfully recreated terrain: {recreated_terrain['name']}")

        except Exception as e:
            print(f"Error recreating terrain from data: {e}")
            traceback.print_exc()

    def _recreate_primitive_from_data(self, obj_data, primitive_data):
        """Recreate primitive from saved primitive data."""
        try:
            primitive_type = primitive_data.get('type', 'cube')

            # Create the appropriate primitive mesh
            if primitive_type == 'cube':
                mesh = trimesh.creation.box(extents=[2.0, 2.0, 2.0])
            elif primitive_type == 'sphere':
                mesh = trimesh.creation.uv_sphere(radius=1.0, count=[32, 16])
            elif primitive_type == 'cone':
                mesh = trimesh.creation.cone(radius=1.0, height=2.0, sections=32)
            elif primitive_type == 'cylinder':
                mesh = trimesh.creation.cylinder(radius=1.0, height=2.0, sections=32)
            elif primitive_type == 'capsule':
                mesh = trimesh.creation.capsule(radius=0.5, height=2.0, count=[32, 16])
            # --- THIS IS THE CRITICAL FIX ---
            elif primitive_type == 'enemy':
                # Enemies are capsule-shaped
                mesh = trimesh.creation.capsule(radius=0.5, height=2.0, count=[32, 16])
            else:
                # Default to cube if unknown type
                mesh = trimesh.creation.box(extents=[2.0, 2.0, 2.0])
                primitive_type = 'cube'

            # Process the mesh for drawing
            identity_transform = np.eye(4, dtype=np.float32)
            self.gl_frame._process_mesh_for_drawing(mesh, identity_transform, obj_data.get('name', primitive_type.capitalize()))

            # Get the newly added object and apply saved properties
            if self.gl_frame.model_draw_list:
                new_obj = self.gl_frame.model_draw_list[-1]

                # Apply saved transform and material properties
                new_obj['position'] = np.array(obj_data['transform']['position'], dtype=np.float32)
                new_obj['rotation'] = np.array(obj_data['transform']['rotation'], dtype=np.float32)
                new_obj['scale'] = np.array(obj_data['transform']['scale'], dtype=np.float32)
                new_obj['base_color_factor'] = obj_data['material']['base_color']
                new_obj['is_transparent'] = obj_data['material'].get('is_transparent', False)
                new_obj['model_file'] = None  # Primitives don't have model files
                new_obj['is_primitive'] = True
                new_obj['primitive_type'] = primitive_type

                # Restore physics properties
                physics_data = obj_data.get('physics', {})
                new_obj['physics_type'] = physics_data.get('type', 'None')
                new_obj['physics_shape'] = physics_data.get('shape', 'Cube')
                new_obj['mass'] = physics_data.get('mass', 1.0)

                # Restore script file
                script_file = obj_data.get('script_file')
                new_obj['script_file'] = script_file

                # Restore enemy-specific properties if this is an enemy
                if primitive_data.get('is_enemy', False) or primitive_type == 'enemy':
                    new_obj['is_enemy'] = True
                    new_obj['enemy_speed'] = primitive_data.get('enemy_speed', 1.0)
                    new_obj['enemy_target'] = None  # Runtime property, reset on load
                    print(f"Successfully recreated enemy with speed {new_obj['enemy_speed']}")
                else:
                    print(f"Successfully recreated {primitive_type} primitive")

        except Exception as e:
            print(f"Error recreating primitive: {e}")
            traceback.print_exc()

    def on_closing(self):
        print("Closing application...")
        if self.gl_frame._after_id:
            self.gl_frame.after_cancel(self.gl_frame._after_id)
        if hasattr(self.gl_frame, 'cleanup_gl_resources'):
             self.gl_frame.cleanup_gl_resources()
        self.destroy()

if __name__ == '__main__':
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = App()
    try:
        app.mainloop()
    finally:
        pygame.quit()
        print("Pygame quit successfully.")
