# Neatoo Common Pitfalls

Consolidated list of common mistakes when working with Neatoo.

## 1. Forgetting to Reassign After Save()

The server deserializes and returns a **new instance**. Always capture the return value:

```csharp
// WRONG - changes lost
await personFactory.Save(person);

// CORRECT
person = await personFactory.Save(person);
```

See: factories.md, blazor-integration.md

## 2. Not Waiting for Async Rules

Async validation rules run in the background. Check `IsBusy` or call `WaitForTasks()` before checking validity:

```csharp
// WRONG - may check validity before async rules complete
if (person.IsValid) { ... }

// CORRECT
await person.WaitForTasks();
if (person.IsValid) { ... }
```

See: rules.md, blazor-integration.md

## 3. Saving Child Entities Directly

Children save through their parent aggregate root. Don't call Save on child factories:

```csharp
// WRONG - children don't have their own Save
await orderLineFactory.Save(lineItem);

// CORRECT - save through aggregate root
order = await orderFactory.Save(order);  // Saves order AND all line items
```

See: aggregates.md, factories.md

## 4. Missing [Remote] Attribute

Server-side operations need `[Remote]` to execute on the server in client-server scenarios:

```csharp
// WRONG - runs on client, can't access database
[Fetch]
public void Fetch(Guid id) { ... }

// CORRECT - runs on server
[Remote]
[Fetch]
public void Fetch(Guid id) { ... }
```

See: client-server.md, factories.md

## 5. Not Handling Null from Fetch

Fetch returns `null` when the entity isn't found. Always check:

```csharp
// WRONG - NullReferenceException if not found
var person = personFactory.Fetch(id);
Console.WriteLine(person.Name);

// CORRECT
var person = personFactory.Fetch(id);
if (person is null)
{
    // Handle not found
    return;
}
```

See: factories.md

## 6. Checking IsValid Instead of IsSavable

`IsSavable` is the comprehensive check for save readiness:

```csharp
// WRONG - doesn't check IsBusy, IsModified, or IsChild
if (person.IsValid) { await Save(); }

// CORRECT - checks IsModified && IsValid && !IsBusy && !IsChild
if (person.IsSavable) { await Save(); }
```

See: entities.md, properties.md, blazor-integration.md

## 7. Modifying Properties During Fetch

Use `LoadProperty` instead of property setters during Fetch to avoid triggering rules:

```csharp
// WRONG - triggers rules during load
[Fetch]
public void Fetch(PersonEntity entity)
{
    Name = entity.Name;  // Triggers validation rules
}

// CORRECT - bypasses rules
[Fetch]
public void Fetch(PersonEntity entity)
{
    LoadProperty(nameof(Name), entity.Name);
}
```

Note: `MapFrom` methods typically use direct assignment since rules are paused during factory operations.

See: data-mapping.md, properties.md

## 8. Circular Reference in Aggregates

Don't create circular parent-child references. Children reference parents, not vice versa in terms of ownership:

```csharp
// WRONG - Order owns LineItems, LineItem owns Order?
public partial IOrder Order { get; set; }  // In LineItem - creates cycle

// CORRECT - Use Parent property (read-only, set by framework)
public IOrder? Parent => GetParent<IOrder>();  // Framework manages this
```

See: aggregates.md

## Quick Checklist

Before saving:
- [ ] Did I reassign after Save()?
- [ ] Did I await WaitForTasks()?
- [ ] Am I saving the aggregate root (not a child)?
- [ ] Did I check IsSavable (not just IsValid)?
- [ ] Do server methods have [Remote]?
- [ ] Did I handle null from Fetch?
