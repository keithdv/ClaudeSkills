# bUnit Getting Started

## Test Project Setup

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <IsPackable>false</IsPackable>
    <IsTestProject>true</IsTestProject>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="bunit" Version="1.31.3" />
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.11.0" />
    <PackageReference Include="xunit" Version="2.9.0" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.8.2" />
    <PackageReference Include="KnockOff" Version="10.3.0" /> <!-- Preferred: type-safe stubs -->
    <PackageReference Include="Moq" Version="4.20.70" /> <!-- Alternative: runtime mocking -->
    <PackageReference Include="Bogus" Version="35.6.0" />
  </ItemGroup>

  <ItemGroup>
    <!-- Reference the Blazor project being tested -->
    <ProjectReference Include="..\MyBlazorApp\MyBlazorApp.csproj" />
  </ItemGroup>
</Project>
```

## Global Usings (_Imports.cs)

```csharp
global using Bunit;
global using Bunit.TestDoubles;
global using Xunit;
global using Moq;
global using Microsoft.Extensions.DependencyInjection;
global using Microsoft.AspNetCore.Components;
```
