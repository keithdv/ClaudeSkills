# Neatoo Aggregates Reference

## What is an Aggregate?

In Domain-Driven Design, an **Aggregate** is a cluster of entities treated as a single unit for data changes. The **Aggregate Root** is the entry point that ensures consistency across the entire cluster.

### Aggregate Characteristics

1. **Single Entry Point** - External code accesses only the root
2. **Transactional Boundary** - All changes saved atomically
3. **Consistency Enforcement** - Root enforces invariants across children
4. **Identity through Root** - Children referenced via root's identity

### Real-World Analogy

An Order with OrderLines is an aggregate:
- Order is the aggregate root
- OrderLines are child entities
- You cannot save an OrderLine independently
- Deleting the Order deletes all lines
- Business rules span the entire order (e.g., "order total must be > $0")

## Defining Aggregates in Neatoo

### Aggregate Root

```csharp
public interface IOrder : IEntityBase
{
    Guid? Id { get; set; }
    string? CustomerName { get; set; }
    DateTime OrderDate { get; set; }
    IOrderLineList? Lines { get; }
    decimal Total { get; }
}

[Factory]
internal partial class Order : EntityBase<Order>, IOrder
{
    private readonly IOrderLineListFactory _lineListFactory;

    public Order(
        IEntityBaseServices<Order> services,
        IOrderLineListFactory lineListFactory) : base(services)
    {
        _lineListFactory = lineListFactory;

        // Rule calculates total from all lines
        RuleManager.AddAction(
            (Order o) => o.Total = o.Lines?.Sum(l => l.LineTotal) ?? 0,
            o => o.Lines);
    }

    public partial Guid? Id { get; set; }
    public partial string? CustomerName { get; set; }
    public partial DateTime OrderDate { get; set; }
    public partial IOrderLineList? Lines { get; set; }
    public partial decimal Total { get; set; }

    [Create]
    public void Create()
    {
        OrderDate = DateTime.Today;
        Lines = _lineListFactory.Create();
    }
}
```

### Child Entity

```csharp
public interface IOrderLine : IEntityBase
{
    Guid? Id { get; set; }
    string? ProductName { get; set; }
    int Quantity { get; set; }
    decimal UnitPrice { get; set; }
    decimal LineTotal { get; }
    IOrder? ParentOrder { get; }
}

[Factory]
internal partial class OrderLine : EntityBase<OrderLine>, IOrderLine
{
    public OrderLine(IEntityBaseServices<OrderLine> services)
        : base(services)
    {
        RuleManager.AddAction(
            (OrderLine l) => l.LineTotal = l.Quantity * l.UnitPrice,
            l => l.Quantity, l => l.UnitPrice);
    }

    public partial Guid? Id { get; set; }
    public partial string? ProductName { get; set; }
    public partial int Quantity { get; set; }
    public partial decimal UnitPrice { get; set; }
    public partial decimal LineTotal { get; set; }

    // Access parent through Parent property
    public IOrder? ParentOrder => Parent as IOrder;
}
```

### Child Collection

```csharp
public interface IOrderLineList : IEntityListBase<IOrderLine>
{
    Task<IOrderLine> AddLine();
    void RemoveLine(IOrderLine line);
    decimal CalculateTotal();
}

[Factory]
internal partial class OrderLineList
    : EntityListBase<IOrderLine>, IOrderLineList
{
    private readonly IOrderLineFactory _lineFactory;

    public OrderLineList(
        IEntityListBaseServices<IOrderLine> services,
        IOrderLineFactory lineFactory) : base(services)
    {
        _lineFactory = lineFactory;
    }

    public async Task<IOrderLine> AddLine()
    {
        var line = await _lineFactory.Create();
        Add(line);
        return line;
    }

    public void RemoveLine(IOrderLine line)
    {
        Remove(line);
    }

    public decimal CalculateTotal()
    {
        return this.Sum(l => l.LineTotal);
    }
}
```

## Parent-Child Relationships

### How Children Get Parents

When you add an entity to a collection, Neatoo automatically:

1. Sets `IsChild = true` on the item
2. Sets `Parent` to the collection's parent (not the collection itself)
3. Raises collection change events

```csharp
var order = await orderFactory.Create();
var line = await order.Lines.AddLine();

// line.IsChild == true
// line.Parent == order (not order.Lines)
// line.ParentOrder == order
```

### Accessing Parent from Child

```csharp
internal partial class OrderLine : EntityBase<OrderLine>, IOrderLine
{
    public IOrder? ParentOrder => Parent as IOrder;

    // Use parent in business logic
    public bool IsEligibleForDiscount()
    {
        return ParentOrder?.CustomerType == CustomerType.VIP;
    }
}
```

### Children Cannot Save Independently

```csharp
var line = await order.Lines.AddLine();
line.ProductName = "Widget";

// WRONG - throws InvalidOperationException
await orderLineFactory.Save(line);

// CORRECT - save through root
await orderFactory.Save(order);
```

The `IsSavable` property returns `false` for children because it includes `!IsChild`.

## Root Property and Aggregate Boundaries

### Finding the Aggregate Root

The `Root` property returns the aggregate root that an entity belongs to:

```csharp
var order = await orderFactory.Create();
var line = await order.Lines.AddLine();
var detail = await line.Details.AddDetail();

order.Root    // null (it IS the root)
line.Root     // order
detail.Root   // order (not line)
```

The computation walks up the `Parent` chain:
- If `Parent` is null → entity is standalone or is the root → `Root` is null
- If `Parent.Root` exists → return it
- If `Parent.Root` is null → Parent is the root → return `Parent`

### Cross-Aggregate Boundary Enforcement

Neatoo prevents accidentally adding an entity from one aggregate to another:

```csharp
var order1 = await orderFactory.Create();
var order2 = await orderFactory.Create();

var line = await order1.Lines.AddLine();

// Later attempt to add to different aggregate
order2.Lines.Add(line);  // THROWS InvalidOperationException
// "Cannot add OrderLine to list: item belongs to aggregate 'Order',
//  but this list belongs to aggregate 'Order'."
```

### Allowed Add Scenarios

| Scenario | item.Root | list.Root | Result |
|----------|-----------|-----------|--------|
| Add brand new item | null | Order | Allowed |
| Add from same aggregate | Order | Order | Allowed |
| Add from different aggregate | Order1 | Order2 | **Throws** |
| Add to root-level list | Order | null | Allowed |

### Deserialization Bypass

The cross-aggregate check is skipped when `IsPaused=true` (during factory operations and JSON deserialization) since data from trusted sources doesn't need validation.

```csharp
// Framework pauses during deserialization
list.FactoryStart(FactoryOperation.Fetch);
list.Add(itemFromDifferentAggregate);  // Allowed when paused
list.FactoryComplete(FactoryOperation.Fetch);
```

## Adding Items to Collections

When adding items to an `EntityListBase<T>`, Neatoo enforces constraints and manages state.

### Constraints

Adding an item throws if any constraint is violated:

| Constraint | Exception | Message |
|------------|-----------|---------|
| Null item | `ArgumentNullException` | - |
| Duplicate | `InvalidOperationException` | "item is already in this list" |
| Busy item | `InvalidOperationException` | "item is busy (async rules running)" |
| Cross-aggregate | `InvalidOperationException` | "item belongs to aggregate 'X', but this list belongs to aggregate 'Y'" |

```csharp
// These all throw:
list.Add(null);                    // ArgumentNullException
list.Add(existingItem);            // Already in list
list.Add(busyItem);                // IsBusy = true
order2.Lines.Add(order1Line);      // Different aggregate
```

### State Changes

When an item is added successfully:

| State | Change |
|-------|--------|
| `Parent` | Set to list's parent (aggregate root) |
| `IsChild` | Set to `true` |
| `IsDeleted` | If `true`, `UnDelete()` called |
| `IsModified` | Existing items (`IsNew=false`) marked modified |
| `ContainingList` | Set to this list (internal) |

### Re-Adding Removed Items

When an existing item is removed then re-added (same list or different list in same aggregate):

```csharp
var line = order.ActiveLines[0];
order.ActiveLines.Remove(line);    // Goes to DeletedList
order.ArchivedLines.Add(line);     // Removes from DeletedList, undeletes
```

### Paused Mode (Deserialization)

During factory operations, constraints are relaxed:
- Duplicate check skipped
- Busy check skipped
- Cross-aggregate check skipped
- `IsChild` not set (factory handles this)

## State Propagation

Meta-properties propagate UP the aggregate hierarchy.

### Propagation Diagram

```
Order (Root)
  IsValid    = IsSelfValid && Lines.IsValid
  IsModified = IsSelfModified || Lines.IsModified
  IsBusy     = IsSelfBusy || Lines.IsBusy

  OrderLineList
    IsValid    = All(line => line.IsValid)
    IsModified = Any(line => line.IsModified) || DeletedList.Any()

    OrderLine 1          OrderLine 2
      IsValid              IsValid
      IsModified           IsModified
```

### Propagation Examples

```csharp
var order = await orderFactory.Create();
order.CustomerName = "John";

// Order is valid (assuming no required fields empty)
// order.IsSelfValid == true
// order.IsValid == true

var line = await order.Lines.AddLine();
// New line has empty required fields
// line.IsValid == false
// order.Lines.IsValid == false
// order.IsValid == false (child invalid)

line.ProductName = "Widget";
line.Quantity = 1;
line.UnitPrice = 9.99m;
// line.IsValid == true
// order.IsValid == true (all children valid)

line.Quantity = 5;
// line.IsModified == true
// order.Lines.IsModified == true
// order.IsModified == true (child modified)
```

## Reacting to Child Changes

### ChildNeatooPropertyChanged

Override to react when any descendant changes:

```csharp
[Factory]
internal partial class Order : EntityBase<Order>, IOrder
{
    protected override Task ChildNeatooPropertyChanged(
        NeatooPropertyChangedEventArgs eventArgs)
    {
        // Recalculate total when line items change
        if (eventArgs.PropertyName == nameof(IOrderLine.Quantity) ||
            eventArgs.PropertyName == nameof(IOrderLine.UnitPrice) ||
            eventArgs.PropertyName == nameof(IOrderLine.LineTotal))
        {
            RecalculateTotal();
        }

        return base.ChildNeatooPropertyChanged(eventArgs);
    }

    private void RecalculateTotal()
    {
        Total = Lines?.Sum(l => l.LineTotal) ?? 0;
    }
}
```

### In Collections - HandleNeatooPropertyChanged

```csharp
[Factory]
internal partial class OrderLineList
    : EntityListBase<IOrderLine>, IOrderLineList
{
    protected override async Task HandleNeatooPropertyChanged(
        NeatooPropertyChangedEventArgs eventArgs)
    {
        await base.HandleNeatooPropertyChanged(eventArgs);

        // Trigger sibling validation for uniqueness
        if (eventArgs.PropertyName == nameof(IOrderLine.ProductName))
        {
            foreach (var sibling in this.Where(l => l != eventArgs.Source))
            {
                await sibling.RunRules(nameof(IOrderLine.ProductName));
            }
        }
    }
}
```

## Cross-Entity Validation

### Rules Accessing Siblings

```csharp
public class UniqueProductRule : RuleBase<IOrderLine>
{
    public UniqueProductRule()
        : base(l => l.ProductName) { }

    protected override IRuleMessages Execute(IOrderLine target)
    {
        var parent = target.Parent as IOrder;
        if (parent?.Lines == null) return None;

        var isDuplicate = parent.Lines
            .Where(l => l != target)
            .Any(l => l.ProductName == target.ProductName);

        return isDuplicate
            ? Error(nameof(target.ProductName), "Product already exists in order")
            : None;
    }
}
```

### Rules Accessing Root

```csharp
public class QuantityLimitRule : RuleBase<IOrderLine>
{
    public QuantityLimitRule()
        : base(l => l.Quantity) { }

    protected override IRuleMessages Execute(IOrderLine target)
    {
        // Use Root to get aggregate root
        var order = target.Root as IOrder;

        // Business rule: VIP customers can order more
        var maxQuantity = order?.CustomerType == CustomerType.VIP ? 1000 : 100;

        return target.Quantity > maxQuantity
            ? Error(nameof(target.Quantity),
                   $"Maximum quantity is {maxQuantity}")
            : None;
    }
}
```

## Saving Aggregates

### Root Save Method

```csharp
[Factory]
internal partial class Order : EntityBase<Order>, IOrder
{
    [Remote]
    [Insert]
    public async Task Insert(
        [Service] IDbContext db,
        [Service] IOrderLineListFactory lineListFactory)
    {
        Id = Guid.NewGuid();

        var entity = new OrderEntity
        {
            Id = Id.Value,
            CustomerName = CustomerName,
            OrderDate = OrderDate
        };

        db.Orders.Add(entity);

        // Save children after parent has ID
        await lineListFactory.Save(Lines, Id.Value);

        await db.SaveChangesAsync();
    }

    [Remote]
    [Update]
    public async Task Update(
        [Service] IDbContext db,
        [Service] IOrderLineListFactory lineListFactory)
    {
        var entity = await db.Orders.FindAsync(Id);

        if (this[nameof(CustomerName)].IsModified)
            entity.CustomerName = CustomerName;
        if (this[nameof(OrderDate)].IsModified)
            entity.OrderDate = OrderDate;

        // Save children (handles inserts, updates, deletes)
        await lineListFactory.Save(Lines, Id.Value);

        await db.SaveChangesAsync();
    }
}
```

### Collection Save Method

```csharp
[Factory]
internal partial class OrderLineList
    : EntityListBase<IOrderLine>, IOrderLineList
{
    [Remote]
    [Update]
    public async Task Update(Guid orderId, [Service] IDbContext db)
    {
        // 1. Process deletions
        foreach (var deleted in DeletedList.Cast<IOrderLine>())
        {
            var entity = await db.OrderLines.FindAsync(deleted.Id);
            if (entity != null)
                db.OrderLines.Remove(entity);
        }

        // 2. Process inserts and updates
        foreach (var line in this)
        {
            if (line.IsNew)
            {
                line.Id = Guid.NewGuid();
                var entity = new OrderLineEntity
                {
                    Id = line.Id.Value,
                    OrderId = orderId,
                    ProductName = line.ProductName,
                    Quantity = line.Quantity,
                    UnitPrice = line.UnitPrice
                };
                db.OrderLines.Add(entity);
            }
            else if (line.IsModified)
            {
                var entity = await db.OrderLines.FindAsync(line.Id);
                if (line[nameof(IOrderLine.ProductName)].IsModified)
                    entity.ProductName = line.ProductName;
                if (line[nameof(IOrderLine.Quantity)].IsModified)
                    entity.Quantity = line.Quantity;
                if (line[nameof(IOrderLine.UnitPrice)].IsModified)
                    entity.UnitPrice = line.UnitPrice;
            }
        }

        await db.SaveChangesAsync();
    }
}
```

## Deep Aggregates

Aggregates can have multiple levels of nesting.

### Three-Level Example

```
Order (Root)
  OrderLineList
    OrderLine
      OrderLineDetailList
        OrderLineDetail
```

```csharp
[Factory]
internal partial class OrderLine : EntityBase<OrderLine>, IOrderLine
{
    public partial IOrderLineDetailList? Details { get; set; }

    [Create]
    public void Create()
    {
        Details = _detailListFactory.Create();
    }
}
```

### Propagation Through All Levels

Changes at any level propagate to the root:

```csharp
var order = await orderFactory.Create();
var line = await order.Lines.AddLine();
var detail = await line.Details.AddDetail();

detail.Description = "Special handling";
// detail.IsModified == true
// line.IsModified == true (child modified)
// order.Lines.IsModified == true
// order.IsModified == true
```

## Delete Behavior

### Deleting Root

```csharp
var order = await orderFactory.Fetch(orderId);
order.Delete();
// order.IsDeleted == true

await orderFactory.Save(order);
// Server [Delete] method called
// Typically cascades to delete children in database
```

### Deleting Child

```csharp
var order = await orderFactory.Fetch(orderId);
order.Lines.RemoveLine(order.Lines[0]);

// If line was persisted (IsNew == false):
//   line moved to DeletedList
//   line.IsDeleted == true
// If line was new (IsNew == true):
//   line simply removed

await orderFactory.Save(order);
// DeletedList processed in collection's Update method
```

### Undelete

```csharp
var order = await orderFactory.Fetch(orderId);
order.Delete();
// User cancels
order.UnDelete();
// order.IsDeleted == false
```

### Delete/Remove Consistency

Calling `entity.Delete()` on an entity in a list is equivalent to calling `list.Remove(entity)`:

```csharp
// These are equivalent:
order.Lines.Remove(line);
line.Delete();
```

Both operations remove from the list, mark as deleted, and add to `DeletedList`.

### Intra-Aggregate Moves

Entities can be moved between lists within the same aggregate:

```csharp
// Company aggregate with two departments
var project = dept1.Projects[0];

// Remove from Dept1
dept1.Projects.Remove(project);
// project in dept1.Projects.DeletedList

// Add to Dept2 (same aggregate root)
dept2.Projects.Add(project);
// project removed from dept1.Projects.DeletedList
// project.IsDeleted = false
// project now in dept2.Projects
```

When an entity is added to a new list within the same aggregate:
1. It's removed from the old list's `DeletedList`
2. It's undeleted (`IsDeleted = false`)
3. It's added to the new list

Cross-aggregate moves throw `InvalidOperationException`.

## Best Practices

### Design Aggregates Around Transactions

An aggregate boundary should match your transaction boundary. If multiple entities must change together atomically, they should be in the same aggregate.

### Keep Aggregates Small

Large aggregates cause performance and concurrency issues. Consider splitting if:
- Loading becomes slow
- Concurrent edit conflicts are common
- Unrelated changes affect each other

### Reference Other Aggregates by ID

```csharp
// GOOD - reference by ID
public partial Guid? CustomerId { get; set; }

// AVOID - direct reference creates large aggregate
// public partial ICustomer? Customer { get; set; }
```

### Enforce Invariants at Root Level

```csharp
public class OrderTotalRule : RuleBase<IOrder>
{
    public OrderTotalRule()
        : base(o => o.Total) { }

    protected override IRuleMessages Execute(IOrder target)
    {
        return target.Total <= 0
            ? Error(nameof(target.Total), "Order total must be greater than zero")
            : None;
    }
}
```

## Common Pitfalls

1. **Saving children directly** - Always save through root
2. **Referencing aggregates directly** - Use IDs for cross-aggregate references
3. **Missing ChildNeatooPropertyChanged** - Override to react to child changes
4. **Not processing DeletedList** - Check collection's DeletedList in Update
5. **Circular references** - Aggregates should form trees, not graphs
6. **Cross-aggregate entity moves** - Adding an entity to a different aggregate throws; intra-aggregate moves (same `Root`) are allowed
